## laneB-bf16kv-300k-baseline (2026-09-22T00:40:30Z)

Lane B: Bluey+Asusi TP2, bf16 KV, max-model-len 300000, GMU 0.85, seqs 8, DFlash 7, marlin, VLLM_USE_DEEP_GEMM=0

Prompt set `v1` (identical across boots), temperature 0, thinking off. Tokens from the server's usage block; TTFT = first token delta.

### Throughput by concurrency (9 categories; the counting ceiling is excluded)

| C | aggregate tok/s | per-stream tok/s | mean TTFT (s) |
|---|---|---|---|
| C1 | 46.35 | 54.72 | 0.378 |
| C2 | 74.08 | 43.78 | 0.386 |
| C3 | 97.33 | 38.23 | 0.42 |
| C4 | 124.82 | 36.75 | 0.424 |
| C5 | 145.24 | 34.43 | 0.454 |
| C6 | 158.86 | 31.62 | 0.483 |

### Per-stream tok/s by category

| category | C1 | C2 | C3 | C4 | C5 | C6 |
|---|---|---|---|---|---|---|
| coding | 73.06 | 49.3 | 49.92 | 47.84 | 45.4 | 41.4 |
| json | 51.44 | 48.96 | 40.7 | 35.59 | 35.8 | 31.86 |
| narrative | 20.73 | 17.3 | 13.98 | 13.04 | 12.32 | 11.59 |
| prose | 25.63 | 19.78 | 17.78 | 15.53 | 14.97 | 13.76 |
| math | 72.58 | 57.69 | 52.87 | 45.13 | 47.03 | 43.09 |
| reasoning | 44.1 | 30.89 | 29.81 | 29.14 | 25.48 | 23.01 |
| summary | 33.57 | 25.89 | 21.79 | 16.02 | 15.5 | 14.37 |
| structured | 80.61 | 67.58 | 56.87 | 53.83 | 48.13 | 47.1 |
| format | 90.73 | 76.59 | 60.38 | 74.66 | 65.2 | 58.43 |
| ceiling_count | 90.04 | 79.12 | 71.66 | 67.5 | 60.13 | 61.37 |

### DFlash accepted tokens per draft step (7 drafted per step)

| category | C1 | C2 | C3 | C4 | C5 | C6 |
|---|---|---|---|---|---|---|
| coding | 5.43 | 5.06 | 5.23 | 5.33 | 5.08 | 5.28 |
| json | 3.8 | 3.71 | 3.65 | 3.63 | 3.68 | 3.57 |
| narrative | 0.7 | 0.79 | 0.74 | 0.81 | 0.84 | 0.83 |
| prose | 1.24 | 1.18 | 1.31 | 1.15 | 1.22 | 1.23 |
| math | 5.26 | 5.02 | 5.16 | 4.86 | 5.09 | 5.02 |
| reasoning | 3.04 | 2.53 | 2.82 | 3.02 | 2.76 | 2.67 |
| summary | 1.97 | 1.95 | 2.05 | 1.47 | 1.56 | 1.5 |
| structured | 6.29 | 5.8 | 6.09 | 6.02 | 6.04 | 6.0 |
| format | 6.73 | 6.45 | 6.08 | 6.68 | 6.52 | 6.23 |
| ceiling_count | 6.82 | 6.82 | 6.82 | 6.82 | 6.87 | 6.82 |

### Cold prefill (unique prefix)

| target | prompt tokens | TTFT (s) | prefill tok/s |
|---|---|---|---|
| 2000 | 2004 | 1.019 | 1966.7 |
| 8000 | 7919 | 4.711 | 1680.9 |
| 32000 | 31836 | 23.929 | 1330.4 |
| 64000 | 63764 | 58.981 | 1081.1 |
| 128000 | 127055 | 157.65 | 805.9 |
| 250000 | 248227 | 458.846 | 541.0 |
