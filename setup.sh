#!/bin/bash
# setup.sh: prepare one DGX Spark for MiMo-V2.6-Flash-RL. Run on BOTH Sparks of the pair.
#   - pulls the vLLM image
#   - downloads the model to $MODEL_DIR (skip with SKIP_DOWNLOAD=1 if the worker reads the head's copy over NFS)
#   - writes a corrected dflash/config.json (the release has a trailing comma) and copies the patched vLLM files to $CACHE
# Uses launch/mimo.env for MODEL_DIR and CACHE.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
ENV_FILE=${ENV_FILE:-$HERE/launch/mimo.env}
[ -f "$ENV_FILE" ] || { cp "$HERE/launch/mimo.env.example" "$ENV_FILE"; echo "created $ENV_FILE: edit HEAD_IP / MODEL_DIR / network, then rerun"; exit 1; }
set -a; . "$ENV_FILE"; set +a
IMAGE=${IMAGE:-ghcr.io/tonyd2wild/vllm-glm53-flash:sm121-v11-dflash2}

echo "== 1/3 image $IMAGE"
docker pull "$IMAGE"

if [ "${SKIP_DOWNLOAD:-0}" != 1 ]; then
  echo "== 2/3 model -> $MODEL_DIR (about 178 GB)"
  mkdir -p "$MODEL_DIR"
  command -v hf >/dev/null || pip install -q -U "huggingface_hub[cli]"
  HF_HUB_DISABLE_XET=1 hf download XiaomiMiMo/MiMo-V2.6-Flash-RL --local-dir "$MODEL_DIR"
else
  echo "== 2/3 model download skipped (SKIP_DOWNLOAD=1)"
fi
[ -f "$MODEL_DIR/config.json" ] || { echo "model not visible at $MODEL_DIR"; exit 3; }

echo "== 3/3 patches -> $CACHE"
mkdir -p "$CACHE"
cp "$HERE"/patches/files/mimo_v2.py "$HERE"/patches/files/mimo_v2_omni.py \
   "$HERE"/patches/files/triton_attn_diffkv.py "$HERE"/patches/files/qwen3_dflash.py "$CACHE/"
python3 - "$MODEL_DIR/dflash/config.json" "$CACHE/dflash-config.fixed.json" <<'PY'
import json, re, sys
src, dst = sys.argv[1], sys.argv[2]
d = json.loads(re.sub(r",(\s*[}\]])", r"\1", open(src).read()))
json.dump(d, open(dst, "w"), indent=2)
print("dflash config ok:", dst, "block_size", d.get("block_size"))
PY
echo "== 3b audio libs (soundfile, PyAV) -> $CACHE/pyextra (the image lacks them; needed for audio input)"
docker run --rm --entrypoint bash -v "$CACHE/pyextra:/out" "$IMAGE" -c "pip install -q --no-deps --root-user-action=ignore --target /out soundfile av && PYTHONPATH=/out python3 -c 'import soundfile, av'" && echo "audio libs ok"

echo "done. Start the worker first:  bash launch/serve.sh 1   (on the worker Spark)"
echo "            then the head:      bash launch/serve.sh 0   (on the head Spark)"
