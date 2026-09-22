# MiMo-V2.6-Flash-RL on 2x NVIDIA DGX Spark (vLLM, TP2, DFlash, image + video + audio)

Xiaomi's [MiMo-V2.6-Flash-RL](https://huggingface.co/XiaomiMiMo/MiMo-V2.6-Flash-RL) (about 310B total, about 12B active, fp8 attention with MXFP4 experts, 1M native context) served on two DGX Sparks (GB10, sm_121) per instance with vLLM tensor parallel 2 and the bundled DFlash drafter. We run two identical pairs side by side on four Sparks.

**Status (2026-09-22):** serving on both pairs with text, image, video and audio input, DFlash speculative decoding (7 draft tokens), 300K max context.
- **Default config:** fp8 KV cache, `--gpu-memory-utilization 0.90`, `--max-model-len 300000`, marlin MXFP4 MoE, DeepGEMM off. **KV pool 1.87M tokens** (12.6 GiB), six full 300K requests at once.
- **FP8 (default) numbers, measured:** 155.8 tok/s aggregate at six streams (code 205.7, tables 248.8, counting 296.4), 53.3 tok/s per stream at one (counting 88.0, tables 84.6, code 70.5, math 68.9, JSON 57.5, prose 25.9), TTFT 0.37 s, cold prefill 1,947 tok/s at 2K down to 656 tok/s at 250K.
- **BF16 KV** (GMU 0.85): same speed within noise, 560K-token pool. Both full benches are below.
- Verified end to end: text, images (16 per request), video (motion direction read correctly from a clip), audio (a spoken password transcribed via both `input_audio` and `audio_url`), needle in a haystack at 100K and 250K tokens (depths 0.1, 0.5, 0.9 at 250K; exact answer every time, about 6.3 min of prefill per 248K-token request).
- Nothing on this page is a projection.

The stock image did not serve this checkpoint correctly on GB10. It took four fixes, all shipped here as drop-in files mounted over the image's copies (see [Patches](#patches)).

## Hardware and image

- 4x DGX Spark (GB10, 121.7 GiB unified memory each), RoCE between them (`enp1s0f0np0`, HCA `rocep1s0f0`).
- Pair A: Reddie (head, 192.168.192.2) + Spark4. Pair B: Bluey (head, 192.168.192.1) + Asusi. Each pair is one TP2 instance.
- Image: `ghcr.io/tonyd2wild/vllm-glm53-flash:sm121-v11-dflash2` (vLLM 0.1.dev20051+g487ecf187, torch 2.13, CUDA 13, sm_120 kernels).
- Weights: 166 GiB, 65 shards, local on each head; the worker of each pair reads the head's copy over read-only NFS.

## Quick start (two DGX Sparks linked over the QSFP port)

```bash
git clone https://github.com/tonyd2wild/MiMo-V2.6-Flash-2x-DGX-Spark && cd MiMo-V2.6-Flash-2x-DGX-Spark
cp launch/mimo.env.example launch/mimo.env   # set HEAD_IP, MODEL_DIR, IFACE/HCA/ADDR_RANGE
bash setup.sh          # on BOTH Sparks: pulls the image, downloads the 178 GB model, stages the patches and audio libs
bash launch/serve.sh 1 # on the worker Spark first
bash launch/serve.sh 0 # on the head Spark; serves http://<head>:8888/v1 after about 11 minutes of loading
```

At GMU 0.90 a restart needs the previous container's memory released first: vLLM probes free memory at startup and refuses if it is below 0.90 of the device (109.5 GiB). `serve.sh` waits for that after removing the old container. The worker needs the model at the same path: its own copy, or the head's folder exported read-only over NFS (then `SKIP_DOWNLOAD=1 bash setup.sh` on the worker). Knobs in `mimo.env` or on the command line: `KV_DTYPE` (`fp8` default, `auto` = bf16), `GMU` (0.90), `MAXLEN` (300000), `SEQS` (8), `SPEC` (`dflash`), `MOE` (`marlin`), `EXTRA_ARGS`. `DFLASH_VSCALE=1` mounts the drafter value-scale patch (measured: no gain, see below). The scripts we run on our own four-Spark fleet are in [examples/tech2wild-fleet](examples/tech2wild-fleet/).

Endpoint: OpenAI-compatible at `http://<head>:8888/v1`, model `mimo-v2.6-flash`. Images go in as `image_url`, video as `video_url`, audio as `input_audio` or `audio_url` (data URLs work for all). The launcher sets the server default to thinking off (`--default-chat-template-kwargs '{"enable_thinking": false}'`, `THINKING=true` to change it); a request can still turn it on with `"chat_template_kwargs": {"enable_thinking": true}`. Without the server default, thinking is on in this chat template and reasoning text can leak into `content` for clients that do not expect it.

## FP8 KV (default config), pair B, 2026-09-22

fp8 KV, max-model-len 300000, GMU 0.90, max-num-seqs 8, DFlash 7, marlin, DeepGEMM off. KV pool 13.89 GiB = 1,835,052 tokens (6.12x at 300K); pair A with the same config reports 1,867,302. This run had the drafter value-scale patch mounted. The same bench on pair A with the stock drafter landed within noise (C1 45.04 / C6 158.46 aggregate, prefill 1,944 at 2K and 925 at 128K), so the patch changes nothing and these numbers stand for the default config. Both runs: [results/fp8-kv-300k-gmu90](results/fp8-kv-300k-gmu90/).

| C | aggregate tok/s | per-stream tok/s | mean TTFT (s) |
|---|---|---|---|
| C1 | 45.58 | 53.31 | 0.367 |
| C2 | 71.03 | 41.61 | 0.425 |
| C3 | 99.69 | 39.04 | 0.405 |
| C4 | 120.37 | 35.35 | 0.419 |
| C5 | 136.47 | 32.68 | 0.463 |
| C6 | 155.77 | 31.16 | 0.498 |

Per-stream tok/s by category:

| category | C1 | C2 | C3 | C4 | C5 | C6 |
|---|---|---|---|---|---|---|
| coding | 70.46 | 54.53 | 48.74 | 45.18 | 41.37 | 40.22 |
| json | 57.45 | 45.53 | 43.10 | 37.12 | 34.94 | 34.06 |
| narrative | 21.91 | 16.67 | 14.79 | 12.30 | 12.44 | 10.80 |
| prose | 25.86 | 19.52 | 16.51 | 15.42 | 14.78 | 14.38 |
| math | 68.92 | 55.54 | 51.69 | 47.79 | 45.67 | 39.28 |
| reasoning | 40.27 | 30.74 | 25.85 | 24.06 | 23.06 | 22.29 |
| summary | 25.57 | 20.60 | 20.48 | 18.58 | 15.64 | 14.85 |
| structured | 84.63 | 61.17 | 60.77 | 52.81 | 49.07 | 51.42 |
| format | 84.68 | 70.15 | 69.45 | 64.88 | 57.19 | 53.14 |
| counting (ceiling) | 87.95 | 76.45 | 68.05 | 63.19 | 57.65 | 53.84 |

Aggregate tok/s at C6 by category: counting 296.4, format 248.8, structured 241.6, coding 205.7, math 205.1, json 170.0, reasoning 123.0, prose 75.6, summary 72.1, narrative 60.0.

DFlash accepted tokens per draft step (of 7) at C1: structured 6.85, counting 6.82, format 6.19, coding 5.23, math 5.00, json 4.00, reasoning 2.62, summary 1.34, prose 1.23, narrative 0.83.

Cold prefill (unique prefix, one request):

| prompt tokens | TTFT (s) | prefill tok/s |
|---|---|---|
| 2,004 | 1.03 | 1,946.6 |
| 7,919 | 4.66 | 1,697.9 |
| 31,836 | 22.35 | 1,424.6 |
| 63,764 | 52.75 | 1,208.8 |
| 127,055 | 135.62 | 936.8 |
| 248,227 | 378.15 | 656.4 |

## Thinking off at the server (both pairs, 2026-09-22)

The shipped default adds `--default-chat-template-kwargs '{"enable_thinking": false}'`. Rebenched both pairs with it (same fp8 config): pair A C1 44.52 / C6 152.65 aggregate tok/s, TTFT 0.398 s; pair B C1 43.93 / C6 159.00, TTFT 0.334 s; cold prefill 1,950 to 1,998 tok/s at 2K and 902 to 935 at 128K. Within noise of the runs above, so the default costs nothing. A plain request with no `chat_template_kwargs` now returns the answer in `content` with empty reasoning on both pairs. Data: [results/fp8-thinking-off](results/fp8-thinking-off/).

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

DFlash accepted tokens per draft step (of 7) at C1: structured 6.29, format 6.73, counting 6.82, coding 5.43, math 5.26, json 3.80, reasoning 3.04, summary 1.97, prose 1.24, narrative 0.70. Prose-type text is where decode is slow; the drafter value-scale patch (04) was tried for it and did not move these numbers.

Cold prefill (unique prefix, one request):

| prompt tokens | TTFT (s) | prefill tok/s |
|---|---|---|
| 2,004 | 1.02 | 1,966.7 |
| 7,919 | 4.71 | 1,680.9 |
| 31,836 | 23.93 | 1,330.4 |
| 63,764 | 58.98 | 1,081.1 |
| 127,055 | 157.65 | 805.9 |
| 248,227 | 458.85 | 541.0 |

## Sampling defaults matter for agent use

Both coding agents we run (OMP and the DeepSeek Harness) send requests without sampling parameters. With vLLM's own defaults (near-greedy) this model would, in a long tool-using session, emit the same tool call hundreds of times inside one response until it hit `max_tokens` (we saw single turns with 148 and 446 identical `grep` calls, and 44-minute turns of repeated `bash` checks). The launcher now passes `--generation-config auto` (the checkpoint's `temperature 1.0`, `top_p 0.95`) plus `--override-generation-config '{"repetition_penalty": 1.05}'` (`REP_PENALTY` knob). After the change the same wait-on-a-background-job task ran as 7 steps with one tool call each. Benchmarks on this page were run at temperature 0 per request and are unaffected. Clients can still set their own sampling per request.

## Patches

All four go in as read-only bind mounts over the image's files (`launch/mimo_node.sh` adds them when present in `/var/tmp/mimo-cache`). Diffs are in [patches/](patches/), full files in [patches/files/](patches/files/).

1. **Fused fp8 QKV loading** (`mimo_v2.py`, patch 01). The checkpoint stores each layer's fused `qkv_proj` pre-sharded for TP4: `num_key_value_heads` (4) chunks, each `[Q_c | K_c | V_c]` with its own 128x128 fp8 block scales (full-attention layers: 108 scale rows, sliding-window layers: 116). The image's loader assumes one chunk per KV head, which is right for the 9 full-attention layers and wrong for the 39 sliding-window layers (8 KV heads), so at TP2 it crashed, and a naive fix scrambled Q/K/V and produced word salad. The patched `_shard_fp8_qkv_proj` takes `ckpt_tp` chunks, gives each rank `ckpt_tp / tp` of them, dequantizes, regroups to `[Q | K | V]` and requantizes. Same approach as upstream [vllm#57508](https://github.com/vllm-project/vllm/pull/57508) and SGLang's MiMo-V2 loader. Verified against the real tensors (exact on SWA layers; 0.7 to 1.1% requantization error on full layers).
2. **Vision class plus DFlash** (`mimo_v2_omni.py`, patch 02). vLLM resolves this checkpoint to `MiMoV2OmniForCausalLM` (vision and audio towers). That class lacked the `SupportsEagle3` marker DFlash needs for auxiliary hidden states. The marker is all it takes: the hooks already delegate to the inner language model.
3. **fp8 KV cache that actually applies** (`mimo_v2.py` + `triton_attn_diffkv.py`, patches 01 and 03). The image's MiMo attention never passed `cache_config`, so `--kv-cache-dtype fp8` silently stayed bf16 on all 48 target layers (only the drafter went fp8). The DiffKV attention backend (192/128 K/V head dims) also rejected quantized KV. Patched: pass `cache_config` (with the sliding window cleared for full-attention layers, since `Attention` otherwise falls back to the model's 128-token window), allow fp8 in the backend and view the cache as fp8 on read. The kernel upcasts K/V to bf16 on load and does not apply KV scales, which is exact for this checkpoint (no calculated scales, unit scales).
4. **DFlash drafter value scale** (`qwen3_dflash.py`, patch 04, opt-in with `DFLASH_VSCALE=1`). The drafter was trained with V scaled by `dflash_config.attention_value_scale` (0.612); the image ignores it. Same change as upstream [vllm#57784](https://github.com/vllm-project/vllm/pull/57784). Measured on the full bench: no change in acceptance or speed in any category, so it is off by default.

Plus three configuration fixes:
- `dflash/config.json` in the release has a trailing comma (invalid JSON). `setup.sh` writes a corrected copy that is mounted over it.
- The image lacks `soundfile` and PyAV, so audio requests fail with "install vllm[audio]". `setup.sh` installs both into `$CACHE/pyextra`, which the launcher puts on `PYTHONPATH`.
- `VLLM_USE_DEEP_GEMM=0` and `--moe-backend marlin`. The image pins DeepGEMM `8b1392b`, which silently corrupts fp8 GEMMs on SM12x ([DeepGEMM#417](https://github.com/deepseek-ai/DeepGEMM/issues/417)); by default vLLM would also route the MXFP4 experts through DeepGEMM.

## How the KV "tokens" figure works here

vLLM's `GPU KV cache size: N tokens` for this hybrid model is `blocks / blocks-per-request x max_model_len`, not raw storage. Sliding-window and drafter layers need a fixed block allocation per request, so the same memory reports more "tokens" at a larger max-model-len. Compare pools at the same max-model-len.

## Tests

- `tests/mimo_test.py <url>`: three prompts, prints TTFT, decode tok/s and the text.
- `tests/mimo_vision.py <url>`: draws a known image locally (red square, blue circle, green triangle, "MIMO 42") and asks for a description.
- `tests/mimo_needle.py <url> 100000,250000 0.1,0.5,0.9`: needle in a haystack at the given sizes and depths.
- `tests/mimo_media.py <url> speech.wav motion.mp4`: audio (two request formats) and video smoke test.
- `tests/mimo_ab.py`: greedy A/B of the two pairs with DFlash acceptance from `/metrics`.
- `bench/mimobench.py`: the full bench (C1 to C6, 9 categories plus a counting ceiling, cold prefill), derived from our DeepSeek-V4.1-Flash bench.

## Open items

- Router `e_score_correction_bias` is held in bf16; the checkpoint and reference use fp32 (quality, not correctness).
- 1M context: not attempted. At 300K the fp8 pool holds six requests; a 1M request would need about 3.3x the per-request blocks.
