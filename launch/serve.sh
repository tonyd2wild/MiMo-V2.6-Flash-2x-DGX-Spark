#!/bin/bash
# serve.sh <rank>: start one rank of a MiMo-V2.6-Flash-RL TP2 pair on this DGX Spark.
#   rank 1 = worker (start it first), rank 0 = head (serves the OpenAI API on $PORT).
# Settings come from launch/mimo.env (copy mimo.env.example). Any variable can also be
# overridden on the command line, e.g.  KV_DTYPE=auto bash launch/serve.sh 0
set -e
R=${1:?usage: serve.sh <rank 0|1>}
HERE=$(cd "$(dirname "$0")" && pwd)
ENV_FILE=${ENV_FILE:-$HERE/mimo.env}
[ -f "$ENV_FILE" ] || { echo "missing $ENV_FILE (copy mimo.env.example and edit it)"; exit 2; }
# command-line environment wins over the file
_saved=$(env | grep -E '^(THINKING|HEAD_IP|MASTER_PORT|MODEL_DIR|CACHE|IFACE|HCA|ADDR_RANGE|PORT|KV_DTYPE|GMU|MAXLEN|SEQS|SPEC|MOE|IMAGE|NAME|EXTRA_ARGS)=' || true)
set -a; . "$ENV_FILE"; set +a
[ -n "$_saved" ] && eval "$(echo "$_saved" | sed 's/^\([A-Z_]*\)=\(.*\)$/\1="\2"/')"

IMAGE=${IMAGE:-ghcr.io/tonyd2wild/vllm-glm53-flash:sm121-v11-dflash2}
NAME=${NAME:-vllm_mimo}
MOE=${MOE:-marlin}
PORT=${PORT:-8888}
: "${HEAD_IP:?set HEAD_IP}" "${MODEL_DIR:?set MODEL_DIR}" "${CACHE:?set CACHE}"
MYIP=$(ip -4 -o addr show "$IFACE" | awk '{print $4}' | cut -d/ -f1)
[ -n "$MYIP" ] || { echo "no IPv4 on $IFACE"; exit 3; }
[ -f "$MODEL_DIR/config.json" ] || { echo "model not found at $MODEL_DIR"; exit 3; }

# Patched files from setup.sh, mounted over the image's copies (see patches/).
V=/usr/local/lib/python3.12/dist-packages/vllm
MOUNTS=()
[ -f "$CACHE/dflash-config.fixed.json" ] && MOUNTS+=(-v "$CACHE/dflash-config.fixed.json:/models/mimo/dflash/config.json:ro")
[ -f "$CACHE/mimo_v2.py" ]              && MOUNTS+=(-v "$CACHE/mimo_v2.py:$V/model_executor/models/mimo_v2.py:ro")
[ -f "$CACHE/mimo_v2_omni.py" ]         && MOUNTS+=(-v "$CACHE/mimo_v2_omni.py:$V/model_executor/models/mimo_v2_omni.py:ro")
[ -f "$CACHE/triton_attn_diffkv.py" ]   && MOUNTS+=(-v "$CACHE/triton_attn_diffkv.py:$V/v1/attention/backends/triton_attn_diffkv.py:ro")
[ "${DFLASH_VSCALE:-0}" = 1 ] && [ -f "$CACHE/qwen3_dflash.py" ] && MOUNTS+=(-v "$CACHE/qwen3_dflash.py:$V/model_executor/models/qwen3_dflash.py:ro")
[ ${#MOUNTS[@]} -ge 8 ] || { echo "patched files missing in $CACHE: run setup.sh first"; exit 4; }

ARGS=(/models/mimo --served-model-name mimo-v2.6-flash --trust-remote-code
  --tensor-parallel-size 2 --distributed-executor-backend mp
  --nnodes 2 --node-rank "$R" --master-addr "$HEAD_IP" --master-port "$MASTER_PORT"
  --gpu-memory-utilization "$GMU" --max-model-len "$MAXLEN" --max-num-seqs "$SEQS"
  --kv-cache-dtype "$KV_DTYPE" --moe-backend "$MOE"
  --host 0.0.0.0 --port "$PORT"
  --reasoning-parser mimo --tool-call-parser mimo --enable-auto-tool-choice
  --default-chat-template-kwargs "{\"enable_thinking\": ${THINKING:-false}}")
[ "$SPEC" = dflash ] && ARGS+=(--speculative-config '{"method":"dflash","model":"/models/mimo/dflash","num_speculative_tokens":7}')
[ "$R" != 0 ] && ARGS+=(--headless)

mkdir -p "$CACHE"
[ -n "${DRY_RUN:-}" ] || docker rm -f "$NAME" > /dev/null 2>&1 || true
# wait for the old container's memory to come back (vLLM refuses to start below GMU x device memory)
if [ -z "${DRY_RUN:-}" ]; then
  # drop the page cache left by the previous weight load: vLLM's startup probe does not count reclaimable cache
  sync; { echo 3 > /proc/sys/vm/drop_caches; } 2>/dev/null || sudo -n sh -c "echo 3 > /proc/sys/vm/drop_caches" 2>/dev/null || echo "could not drop caches (need root); startup may refuse at GMU $GMU"
  need=$(python3 -c "print(int(121.69*$GMU*1024*1.01))"); for i in $(seq 1 30); do
    avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo); [ "$avail" -ge "$need" ] && break; sleep 5; done
  echo "MemAvailable ${avail} MiB (need about ${need} for GMU $GMU)"
fi
# shellcheck disable=SC2086
${DRY_RUN:+echo} docker run -d --name "$NAME" --gpus all --network host --ipc host --shm-size 32g \
  --memory 112g --memory-swap 112g --ulimit memlock=-1:-1 --cap-add IPC_LOCK --device /dev/infiniband:/dev/infiniband \
  -v "$MODEL_DIR:/models/mimo:ro" -v "$CACHE:/cache" "${MOUNTS[@]}" \
  -e HF_HOME=/cache/huggingface -e HF_HUB_OFFLINE=1 -e VLLM_CACHE_ROOT=/cache/vllm-mimo -e TRITON_CACHE_DIR=/cache/triton \
  -e VLLM_ENGINE_READY_TIMEOUT_S=3600 -e TORCH_CUDA_ARCH_LIST=12.1a -e VLLM_HOST_IP="$MYIP" \
  -e PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True -e VLLM_USE_DEEP_GEMM=0 \
  -e PYTHONPATH=/cache/pyextra \
  -e NCCL_NET=IB -e NCCL_IB_DISABLE=0 -e NCCL_IB_HCA="$HCA" -e NCCL_IB_GID_INDEX=3 -e NCCL_IB_ROCE_VERSION_NUM=2 \
  -e NCCL_IB_ADDR_FAMILY=AF_INET -e NCCL_IB_ADDR_RANGE="$ADDR_RANGE" -e NCCL_SOCKET_IFNAME="$IFACE" \
  -e GLOO_SOCKET_IFNAME="$IFACE" -e NCCL_CROSS_NIC=0 -e NCCL_NVLS_ENABLE=0 -e NCCL_IB_MERGE_NICS=0 \
  -e NCCL_CUMEM_ENABLE=0 -e NCCL_IGNORE_CPU_AFFINITY=1 -e NCCL_DEBUG=WARN -e TORCH_NCCL_ASYNC_ERROR_HANDLING=1 \
  "$IMAGE" "${ARGS[@]}" ${EXTRA_ARGS:-}
echo "started $NAME rank=$R on $(hostname) ($MYIP) head=$HEAD_IP:$MASTER_PORT kv=$KV_DTYPE gmu=$GMU maxlen=$MAXLEN spec=$SPEC"
[ "$R" = 0 ] && echo "weights load in about 11 minutes; watch: docker logs -f $NAME ; ready when curl -s localhost:$PORT/v1/models lists mimo-v2.6-flash"
