#!/bin/bash
# mimo_node.sh <A|B> <rank 0|1> : one node of a MiMo-V2.6-Flash-RL TP2 instance (vLLM, DFlash).
#   A = head Reddie 192.168.192.2 + worker Spark4 ; B = head Bluey 192.168.192.1 + worker Asusi.
# Image: Tony's GB10 vLLM image (MiMo-V2 + DFlash support, sm_120 kernels, CUDA 13). Knobs from the environment.
set -e
PAIR=${1:?A or B}; R=${2:?rank 0 or 1}
IMAGE=${IMAGE:-ghcr.io/tonyd2wild/vllm-glm53-flash:sm121-v11-dflash2}
NAME=${NAME:-vllm_mimo}
case $PAIR in
  A) HEAD=192.168.192.2; DPORT=${DPORT:-29650};;
  B) HEAD=192.168.192.1; DPORT=${DPORT:-29660};;
  *) echo "pair must be A or B"; exit 2;;
esac
MYIP=$(ip -4 -o addr show enp1s0f0np0 | awk '{print $4}' | cut -d/ -f1)
if [ -d /var/tmp/models/MiMo-V2.6-Flash-RL ] && [ -f /var/tmp/models/MiMo-V2.6-Flash-RL/config.json ]; then
  HOST_MODEL=/var/tmp/models/MiMo-V2.6-Flash-RL
else
  HOST_MODEL=/mnt/reddie-models/MiMo-V2.6-Flash-RL
fi
[ -f "$HOST_MODEL/config.json" ] || { echo "model not visible at $HOST_MODEL"; exit 3; }
CACHE=${CACHE:-/var/tmp/mimo-cache}
mkdir -p "$CACHE"
# the published dflash/config.json has a trailing comma (invalid JSON); mount a corrected copy over it
DFLASH_FIX=""
[ -f "$CACHE/dflash-config.fixed.json" ] && DFLASH_FIX="-v $CACHE/dflash-config.fixed.json:/models/mimo/dflash/config.json:ro"
# fused fp8 qkv_proj is pre-sharded in num_key_value_heads (4) chunks; stock loader assumes one chunk per KV head (vllm#57508)
[ -f "$CACHE/mimo_v2.py" ] && DFLASH_FIX="$DFLASH_FIX -v $CACHE/mimo_v2.py:/usr/local/lib/python3.12/dist-packages/vllm/model_executor/models/mimo_v2.py:ro"
# Omni wrapper lacks the SupportsEagle3 marker DFlash needs (its hooks already delegate to language_model)
[ -f "$CACHE/mimo_v2_omni.py" ] && DFLASH_FIX="$DFLASH_FIX -v $CACHE/mimo_v2_omni.py:/usr/local/lib/python3.12/dist-packages/vllm/model_executor/models/mimo_v2_omni.py:ro"
# DiffKV attention backend (MiMo 192/128 heads) with fp8 KV enabled (stock rejects quantized KV)
[ -f "$CACHE/triton_attn_diffkv.py" ] && DFLASH_FIX="$DFLASH_FIX -v $CACHE/triton_attn_diffkv.py:/usr/local/lib/python3.12/dist-packages/vllm/v1/attention/backends/triton_attn_diffkv.py:ro"
# DFlash drafter value scale (dflash_config.attention_value_scale, upstream vllm#57784); opt-in until measured
[ "${DFLASH_VSCALE:-0}" = 1 ] && [ -f "$CACHE/qwen3_dflash.py" ] && DFLASH_FIX="$DFLASH_FIX -v $CACHE/qwen3_dflash.py:/usr/local/lib/python3.12/dist-packages/vllm/model_executor/models/qwen3_dflash.py:ro"
MAXLEN=${MAXLEN:-300000}
GMU=${GMU:-0.90}
SEQS=${SEQS:-8}
SPEC=${SPEC:-dflash}
KV_DTYPE=${KV_DTYPE:-fp8}   # fp8 (default) or auto (= bf16)
MOE=${MOE:-marlin}
EXTRA_ARGS=${EXTRA_ARGS:-}
ARGS=(/models/mimo --served-model-name mimo-v2.6-flash --trust-remote-code
  --tensor-parallel-size 2 --distributed-executor-backend mp
  --nnodes 2 --node-rank "$R" --master-addr "$HEAD" --master-port "$DPORT"
  --gpu-memory-utilization "$GMU" --max-model-len "$MAXLEN" --max-num-seqs "$SEQS"
  --host 0.0.0.0 --port 8888
  --kv-cache-dtype "$KV_DTYPE" --moe-backend "$MOE"
  --reasoning-parser mimo --tool-call-parser mimo --enable-auto-tool-choice
  --default-chat-template-kwargs "{\"enable_thinking\": ${THINKING:-false}}"
  --generation-config auto --override-generation-config "{\"repetition_penalty\": ${REP_PENALTY:-1.05}}")
[ "$SPEC" = dflash ] && ARGS+=(--speculative-config '{"method":"dflash","model":"/models/mimo/dflash","num_speculative_tokens":7}')
[ "$R" != 0 ] && ARGS+=(--headless)
docker rm -f "$NAME" > /dev/null 2>&1 || true
# at GMU 0.90 the startup probe needs the page cache from the previous load gone (Kai: drop_caches is not optional)
sync; { echo 3 > /proc/sys/vm/drop_caches; } 2>/dev/null || sudo -n sh -c "echo 3 > /proc/sys/vm/drop_caches" 2>/dev/null || true
# shellcheck disable=SC2086
docker run -d --name "$NAME" --gpus all --network host --ipc host --shm-size 32g \
  --memory 112g --memory-swap 112g --ulimit memlock=-1:-1 --cap-add IPC_LOCK --device /dev/infiniband:/dev/infiniband \
  -v "$HOST_MODEL:/models/mimo:ro" -v "$CACHE:/cache" $DFLASH_FIX \
  -e HF_HOME=/cache/huggingface -e HF_HUB_OFFLINE=1 -e VLLM_CACHE_ROOT=/cache/vllm-mimo -e TRITON_CACHE_DIR=/cache/triton \
  -e VLLM_ENGINE_READY_TIMEOUT_S=3600 -e TORCH_CUDA_ARCH_LIST=12.1a -e VLLM_HOST_IP="$MYIP" \
  -e PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
  -e PYTHONPATH=/cache/pyextra \
  -e VLLM_USE_DEEP_GEMM=${VLLM_USE_DEEP_GEMM:-0} \
  -e NCCL_NET=IB -e NCCL_IB_DISABLE=0 -e NCCL_IB_HCA=rocep1s0f0 -e NCCL_IB_GID_INDEX=3 -e NCCL_IB_ROCE_VERSION_NUM=2 \
  -e NCCL_IB_ADDR_FAMILY=AF_INET -e NCCL_IB_ADDR_RANGE=192.168.192.0/24 -e NCCL_SOCKET_IFNAME=enp1s0f0np0 \
  -e GLOO_SOCKET_IFNAME=enp1s0f0np0 -e NCCL_CROSS_NIC=0 -e NCCL_NVLS_ENABLE=0 -e NCCL_IB_MERGE_NICS=0 \
  -e NCCL_CUMEM_ENABLE=0 -e NCCL_IGNORE_CPU_AFFINITY=1 -e NCCL_DEBUG=WARN -e TORCH_NCCL_ASYNC_ERROR_HANDLING=1 \
  "$IMAGE" "${ARGS[@]}" $EXTRA_ARGS
echo "started $NAME pair=$PAIR rank=$R on $(hostname) ($MYIP) head=$HEAD:$DPORT model=$HOST_MODEL maxlen=$MAXLEN gmu=$GMU kv=$KV_DTYPE moe=$MOE seqs=$SEQS spec=$SPEC dflash_vscale=${DFLASH_VSCALE:-0}"
