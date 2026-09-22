# MiMo-V2.6-Flash-RL on 2x NVIDIA DGX Spark (vLLM, TP2, DFlash, vision + audio)

Xiaomi's [MiMo-V2.6-Flash-RL](https://huggingface.co/XiaomiMiMo/MiMo-V2.6-Flash-RL) (about 310B total, about 12B active, fp8 attention with MXFP4 experts, 1M native context) served on two DGX Sparks (GB10, sm_121) per instance with vLLM tensor parallel 2 and the bundled DFlash drafter. We run two identical pairs side by side on four Sparks.

**Status (2026-09-22):** serving on both pairs with text, image and audio input, DFlash speculative decoding (7 draft tokens), 300K max context.
- **Default config:** fp8 KV cache, `--gpu-memory-utilization 0.90`, `--max-model-len 300000`, marlin MXFP4 MoE, DeepGEMM off.
- **BF16 baseline (measured, below):** 158.9 tok/s aggregate at six streams, 54.7 tok/s per stream at one, cold prefill 1,967 tok/s at 2K down to 541 tok/s at 250K.
- **FP8 baseline:** being measured, added here when done.
- Nothing on this page is a projection.

The stock image did not serve this checkpoint correctly on GB10. It took four fixes, all shipped here as drop-in files mounted over the image's copies (see [Patches](#patches)).

## Hardware and image

- 4x DGX Spark (GB10, 121.7 GiB unified memory each), RoCE between them (`enp1s0f0np0`, HCA `rocep1s0f0`).
- Pair A: Reddie (head, 192.168.192.2) + Spark4. Pair B: Bluey (head, 192.168.192.1) + Asusi. Each pair is one TP2 instance.
- Image: `ghcr.io/tonyd2wild/vllm-glm53-flash:sm121-v11-dflash2` (vLLM 0.1.dev20051+g487ecf187, torch 2.13, CUDA 13, sm_120 kernels).
- Weights: 166 GiB, 65 shards, local on each head; the worker of each pair reads the head's copy over read-only NFS.

## Quick start

```bash
# on each node: fix the drafter config once (writes /var/tmp/mimo-cache/dflash-config.fixed.json)
bash launch/fix_dflash_cfg.sh
# copy patches/files/*.py to /var/tmp/mimo-cache/ on every node, then per pair, worker first:
bash launch/mimo_node.sh A 1     # on Spark4
bash launch/mimo_node.sh A 0     # on Reddie (head, serves :8888)
# or start both pairs from Reddie: bash launch/mimo_up.sh <label>
```

Knobs (environment): `KV_DTYPE` (`fp8` default, `auto` = bf16), `GMU` (0.90), `MAXLEN` (300000), `SEQS` (8), `SPEC` (`dflash`), `MOE` (`marlin`), `DFLASH_VSCALE` (0; 1 mounts the drafter value-scale fix, under test), `EXTRA_ARGS`.

Endpoint: OpenAI-compatible at `http://<head>:8888/v1`, model `mimo-v2.6-flash`. Images go in as `image_url` (data URLs work). Thinking is on by default in the chat template; pass `"chat_template_kwargs": {"enable_thinking": false}` to turn it off.

## BF16 KV baseline (pair B, 2026-09-22)

bf16 KV, max-model-len 300000, GMU 0.85, max-num-seqs 8, DFlash 7, marlin, DeepGEMM off. KV pool 7.71 GiB = 560,063 tokens (1.87x at 300K). Prompt set v1, temperature 0, thinking off, unique prefix per request (no prefix-cache hits). Full data: [results/bf16-kv-300k](results/bf16-kv-300k/).

| C | aggregate tok/s | per-stream tok/s | mean TTFT (s) |
|---|---|---|---|
| C1 | 46.35 | 54.72 | 0.378 |
| C2 | 74.08 | 43.78 | 0.386 |
| C3 | 97.33 | 38.23 | 0.420 |
| C4 | 124.82 | 36.75 | 0.424 |
| C5 | 145.24 | 34.43 | 0.454 |
| C6 | 158.86 | 31.62 | 0.483 |

Per-stream tok/s by category:

| category | C1 | C2 | C3 | C4 | C5 | C6 |
|---|---|---|---|---|---|---|
| coding | 73.06 | 49.30 | 49.92 | 47.84 | 45.40 | 41.40 |
| json | 51.44 | 48.96 | 40.70 | 35.59 | 35.80 | 31.86 |
| narrative | 20.73 | 17.30 | 13.98 | 13.04 | 12.32 | 11.59 |
| prose | 25.63 | 19.78 | 17.78 | 15.53 | 14.97 | 13.76 |
| math | 72.58 | 57.69 | 52.87 | 45.13 | 47.03 | 43.09 |
| reasoning | 44.10 | 30.89 | 29.81 | 29.14 | 25.48 | 23.01 |
| summary | 33.57 | 25.89 | 21.79 | 16.02 | 15.50 | 14.37 |
| structured | 80.61 | 67.58 | 56.87 | 53.83 | 48.13 | 47.10 |
| format | 90.73 | 76.59 | 60.38 | 74.66 | 65.20 | 58.43 |
| counting (ceiling) | 90.04 | 79.12 | 71.66 | 67.50 | 60.13 | 61.37 |

DFlash accepted tokens per draft step (of 7) at C1: structured 6.29, format 6.73, counting 6.82, coding 5.43, math 5.26, json 3.80, reasoning 3.04, summary 1.97, prose 1.24, narrative 0.70. Prose-type text is where decode is slow, and the drafter value-scale fix (patch 04) targets it.

Cold prefill (unique prefix, one request):

| prompt tokens | TTFT (s) | prefill tok/s |
|---|---|---|
| 2,004 | 1.02 | 1,966.7 |
| 7,919 | 4.71 | 1,680.9 |
| 31,836 | 23.93 | 1,330.4 |
| 63,764 | 58.98 | 1,081.1 |
| 127,055 | 157.65 | 805.9 |
| 248,227 | 458.85 | 541.0 |

## FP8 KV baseline

Pending. Same bench, pair A, fp8 KV, GMU 0.90.

## Patches

All four go in as read-only bind mounts over the image's files (`launch/mimo_node.sh` adds them when present in `/var/tmp/mimo-cache`). Diffs are in [patches/](patches/), full files in [patches/files/](patches/files/).

1. **Fused fp8 QKV loading** (`mimo_v2.py`, patch 01). The checkpoint stores each layer's fused `qkv_proj` pre-sharded for TP4: `num_key_value_heads` (4) chunks, each `[Q_c | K_c | V_c]` with its own 128x128 fp8 block scales (full-attention layers: 108 scale rows, sliding-window layers: 116). The image's loader assumes one chunk per KV head, which is right for the 9 full-attention layers and wrong for the 39 sliding-window layers (8 KV heads), so at TP2 it crashed, and a naive fix scrambled Q/K/V and produced word salad. The patched `_shard_fp8_qkv_proj` takes `ckpt_tp` chunks, gives each rank `ckpt_tp / tp` of them, dequantizes, regroups to `[Q | K | V]` and requantizes. Same approach as upstream [vllm#57508](https://github.com/vllm-project/vllm/pull/57508) and SGLang's MiMo-V2 loader. Verified against the real tensors (exact on SWA layers; 0.7 to 1.1% requantization error on full layers).
2. **Vision class plus DFlash** (`mimo_v2_omni.py`, patch 02). vLLM resolves this checkpoint to `MiMoV2OmniForCausalLM` (vision and audio towers). That class lacked the `SupportsEagle3` marker DFlash needs for auxiliary hidden states. The marker is all it takes: the hooks already delegate to the inner language model.
3. **fp8 KV cache that actually applies** (`mimo_v2.py` + `triton_attn_diffkv.py`, patches 01 and 03). The image's MiMo attention never passed `cache_config`, so `--kv-cache-dtype fp8` silently stayed bf16 on all 48 target layers (only the drafter went fp8). The DiffKV attention backend (192/128 K/V head dims) also rejected quantized KV. Patched: pass `cache_config` (with the sliding window cleared for full-attention layers, since `Attention` otherwise falls back to the model's 128-token window), allow fp8 in the backend and view the cache as fp8 on read. The kernel upcasts K/V to bf16 on load and does not apply KV scales, which is exact for this checkpoint (no calculated scales, unit scales).
4. **DFlash drafter value scale** (`qwen3_dflash.py`, patch 04, opt-in with `DFLASH_VSCALE=1`, under test). The drafter was trained with V scaled by `dflash_config.attention_value_scale` (0.612); the image ignores it. Same change as upstream [vllm#57784](https://github.com/vllm-project/vllm/pull/57784).

Plus two configuration fixes:
- `dflash/config.json` in the release has a trailing comma (invalid JSON). `launch/fix_dflash_cfg.sh` writes a corrected copy that is mounted over it.
- `VLLM_USE_DEEP_GEMM=0` and `--moe-backend marlin`. The image pins DeepGEMM `8b1392b`, which silently corrupts fp8 GEMMs on SM12x ([DeepGEMM#417](https://github.com/deepseek-ai/DeepGEMM/issues/417)); by default vLLM would also route the MXFP4 experts through DeepGEMM.

## How the KV "tokens" figure works here

vLLM's `GPU KV cache size: N tokens` for this hybrid model is `blocks / blocks-per-request x max_model_len`, not raw storage. Sliding-window and drafter layers need a fixed block allocation per request, so the same memory reports more "tokens" at a larger max-model-len. Compare pools at the same max-model-len.

## Tests

- `tests/mimo_test.py <url>`: three prompts, prints TTFT, decode tok/s and the text.
- `tests/mimo_vision.py <url>`: draws a known image locally (red square, blue circle, green triangle, "MIMO 42") and asks for a description.
- `tests/mimo_needle.py <url> 100000,250000 0.1,0.5,0.9`: needle in a haystack at the given sizes and depths.
- `tests/mimo_ab.py`: greedy A/B of the two pairs with DFlash acceptance from `/metrics`.
- `bench/mimobench.py`: the full bench (C1 to C6, 9 categories plus a counting ceiling, cold prefill), derived from our DeepSeek-V4.1-Flash bench.

## Open items

- Router `e_score_correction_bias` is held in bf16; the checkpoint and reference use fp32 (quality, not correctness).
- Audio input loads but has not been tested end to end.
- 1M context: needs a larger pool than 300K at GMU 0.90 gives; not attempted yet.
