## laneA-fp8kv-gmu90-baseline (2026-09-22T01:43:05Z)

Lane A: Reddie+Spark4 TP2, fp8 KV (real), max-model-len 300000, GMU 0.90, seqs 8, DFlash 7 (stock drafter), marlin, VLLM_USE_DEEP_GEMM=0. KV pool 1,867,302 tokens.

Prompt set `v1` (identical across boots), temperature 0, thinking off. Tokens from the server's usage block; TTFT = first token delta.

### Throughput by concurrency (9 categories; the counting ceiling is excluded)

| C | aggregate tok/s | per-stream tok/s | mean TTFT (s) |
|---|---|---|---|
| C1 | 45.04 | 52.37 | 0.349 |
| C2 | 73.25 | 43.06 | 0.375 |
| C3 | 99.0 | 38.91 | 0.388 |
| C4 | 121.2 | 36.03 | 0.416 |
| C5 | 142.94 | 33.86 | 0.456 |
| C6 | 158.46 | 31.33 | 0.483 |

### Per-stream tok/s by category

| category | C1 | C2 | C3 | C4 | C5 | C6 |
|---|---|---|---|---|---|---|
| coding | 72.69 | 58.64 | 49.3 | 52.31 | 42.79 | 39.3 |
| json | 50.31 | 42.26 | 41.0 | 33.93 | 33.69 | 31.59 |
| narrative | 21.03 | 17.41 | 14.82 | 13.21 | 12.48 | 11.64 |
| prose | 24.34 | 19.91 | 17.56 | 15.87 | 14.77 | 13.07 |
| math | 66.11 | 51.3 | 48.76 | 50.14 | 45.76 | 42.48 |
| reasoning | 43.76 | 32.18 | 27.77 | 25.03 | 23.34 | 22.66 |
| summary | 29.24 | 20.13 | 18.44 | 18.06 | 14.79 | 15.4 |
| structured | 78.9 | 69.33 | 67.71 | 51.57 | 53.16 | 47.53 |
| format | 84.99 | 76.36 | 64.85 | 64.11 | 63.92 | 58.29 |
| ceiling_count | 89.79 | 77.01 | 69.39 | 64.97 | 60.88 | 57.95 |

### DFlash accepted tokens per draft step (7 drafted per step)

| category | C1 | C2 | C3 | C4 | C5 | C6 |
|---|---|---|---|---|---|---|
| coding | 5.52 | 5.39 | 5.21 | 5.38 | 5.3 | 5.15 |
| json | 3.41 | 3.65 | 3.88 | 3.81 | 3.75 | 3.48 |
| narrative | 0.73 | 0.84 | 0.82 | 0.81 | 0.82 | 0.86 |
| prose | 1.09 | 1.17 | 1.23 | 1.17 | 1.21 | 1.09 |
| math | 4.63 | 4.79 | 4.96 | 5.02 | 5.09 | 4.99 |
| reasoning | 2.98 | 2.71 | 2.71 | 2.71 | 2.65 | 2.8 |
| summary | 1.58 | 1.44 | 1.46 | 1.63 | 1.43 | 1.66 |
| structured | 6.29 | 6.25 | 6.79 | 6.09 | 6.39 | 6.23 |
| format | 6.25 | 6.22 | 6.1 | 6.23 | 6.21 | 6.21 |
| ceiling_count | 6.82 | 6.82 | 6.82 | 6.82 | 6.82 | 6.82 |

### Cold prefill (unique prefix)

| target | prompt tokens | TTFT (s) | prefill tok/s |
|---|---|---|---|
| 2000 | 2004 | 1.031 | 1943.8 |
| 8000 | 7919 | 4.62 | 1714.2 |
| 32000 | 31836 | 22.085 | 1441.5 |
| 64000 | 63764 | 52.159 | 1222.5 |
| 128000 | 127055 | 137.332 | 925.2 |
| 250000 | 248227 | 378.087 | 656.5 |
