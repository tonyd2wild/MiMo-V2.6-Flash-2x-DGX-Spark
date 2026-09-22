## laneB-fp8kv-gmu90-dflash-vscale (2026-09-22T01:33:10Z)

Lane B: Bluey+Asusi TP2, fp8 KV (real), max-model-len 300000, GMU 0.90, seqs 8, DFlash 7 + drafter value-scale patch, marlin, VLLM_USE_DEEP_GEMM=0. KV pool 1,835,052 tokens.

Prompt set `v1` (identical across boots), temperature 0, thinking off. Tokens from the server's usage block; TTFT = first token delta.

### Throughput by concurrency (9 categories; the counting ceiling is excluded)

| C | aggregate tok/s | per-stream tok/s | mean TTFT (s) |
|---|---|---|---|
| C1 | 45.58 | 53.31 | 0.367 |
| C2 | 71.03 | 41.61 | 0.425 |
| C3 | 99.69 | 39.04 | 0.405 |
| C4 | 120.37 | 35.35 | 0.419 |
| C5 | 136.47 | 32.68 | 0.463 |
| C6 | 155.77 | 31.16 | 0.498 |

### Per-stream tok/s by category

| category | C1 | C2 | C3 | C4 | C5 | C6 |
|---|---|---|---|---|---|---|
| coding | 70.46 | 54.53 | 48.74 | 45.18 | 41.37 | 40.22 |
| json | 57.45 | 45.53 | 43.1 | 37.12 | 34.94 | 34.06 |
| narrative | 21.91 | 16.67 | 14.79 | 12.3 | 12.44 | 10.8 |
| prose | 25.86 | 19.52 | 16.51 | 15.42 | 14.78 | 14.38 |
| math | 68.92 | 55.54 | 51.69 | 47.79 | 45.67 | 39.28 |
| reasoning | 40.27 | 30.74 | 25.85 | 24.06 | 23.06 | 22.29 |
| summary | 25.57 | 20.6 | 20.48 | 18.58 | 15.64 | 14.85 |
| structured | 84.63 | 61.17 | 60.77 | 52.81 | 49.07 | 51.42 |
| format | 84.68 | 70.15 | 69.45 | 64.88 | 57.19 | 53.14 |
| ceiling_count | 87.95 | 76.45 | 68.05 | 63.19 | 57.65 | 53.84 |

### DFlash accepted tokens per draft step (7 drafted per step)

| category | C1 | C2 | C3 | C4 | C5 | C6 |
|---|---|---|---|---|---|---|
| coding | 5.23 | 5.41 | 5.27 | 5.31 | 5.42 | 5.29 |
| json | 4.0 | 4.09 | 4.02 | 3.81 | 4.09 | 3.88 |
| narrative | 0.83 | 0.79 | 0.86 | 0.75 | 0.86 | 0.77 |
| prose | 1.23 | 1.13 | 1.2 | 1.2 | 1.26 | 1.38 |
| math | 5.0 | 4.62 | 4.98 | 4.81 | 4.97 | 4.74 |
| reasoning | 2.62 | 2.7 | 2.41 | 2.6 | 2.63 | 2.78 |
| summary | 1.34 | 1.59 | 1.89 | 1.72 | 1.69 | 1.66 |
| structured | 6.85 | 6.03 | 6.62 | 6.16 | 6.36 | 6.45 |
| format | 6.19 | 6.03 | 6.25 | 6.22 | 6.15 | 6.1 |
| ceiling_count | 6.82 | 6.82 | 6.82 | 6.82 | 6.84 | 6.84 |

### Cold prefill (unique prefix)

| target | prompt tokens | TTFT (s) | prefill tok/s |
|---|---|---|---|
| 2000 | 2004 | 1.03 | 1946.6 |
| 8000 | 7919 | 4.664 | 1697.9 |
| 32000 | 31836 | 22.348 | 1424.6 |
| 64000 | 63764 | 52.752 | 1208.8 |
| 128000 | 127055 | 135.621 | 936.8 |
| 250000 | 248227 | 378.145 | 656.4 |
