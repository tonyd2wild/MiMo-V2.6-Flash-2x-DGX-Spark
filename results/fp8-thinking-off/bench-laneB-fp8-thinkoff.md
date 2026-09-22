## laneB-fp8-thinkoff (2026-09-22T02:43:45Z)

Lane B fp8 KV GMU 0.90 300K, server default enable_thinking=false, audio libs. Clean rerun; the first attempt shared the lane with interactive use.

Prompt set `v1` (identical across boots), temperature 0, thinking off. Tokens from the server's usage block; TTFT = first token delta.

### Throughput by concurrency (9 categories; the counting ceiling is excluded)

| C | aggregate tok/s | per-stream tok/s | mean TTFT (s) |
|---|---|---|---|
| C1 | 43.93 | 50.8 | 0.334 |
| C2 | 72.06 | 42.05 | 0.368 |
| C3 | 94.47 | 37.28 | 0.367 |
| C4 | 118.29 | 35.5 | 0.392 |
| C5 | 135.51 | 32.68 | 0.434 |
| C6 | 159.0 | 31.56 | 0.476 |

### Per-stream tok/s by category

| category | C1 | C2 | C3 | C4 | C5 | C6 |
|---|---|---|---|---|---|---|
| coding | 67.37 | 52.1 | 51.88 | 42.7 | 39.25 | 39.7 |
| json | 51.09 | 38.94 | 35.6 | 36.38 | 34.05 | 32.28 |
| narrative | 20.07 | 16.05 | 14.59 | 13.25 | 11.85 | 11.02 |
| prose | 27.61 | 20.31 | 17.02 | 16.0 | 13.92 | 13.27 |
| math | 67.38 | 57.08 | 45.83 | 46.93 | 41.65 | 42.12 |
| reasoning | 35.44 | 34.78 | 28.4 | 24.29 | 24.14 | 21.28 |
| summary | 29.1 | 23.59 | 19.01 | 17.86 | 15.06 | 14.28 |
| structured | 79.44 | 64.09 | 60.49 | 61.24 | 53.83 | 53.31 |
| format | 79.67 | 71.54 | 62.7 | 60.83 | 60.36 | 56.81 |
| ceiling_count | 94.56 | 76.01 | 68.23 | 60.05 | 57.51 | 54.97 |

### DFlash accepted tokens per draft step (7 drafted per step)

| category | C1 | C2 | C3 | C4 | C5 | C6 |
|---|---|---|---|---|---|---|
| coding | 5.03 | 5.06 | 5.49 | 4.91 | 5.0 | 5.14 |
| json | 3.41 | 3.56 | 3.66 | 3.65 | 3.71 | 3.7 |
| narrative | 0.65 | 0.71 | 0.78 | 0.83 | 0.76 | 0.79 |
| prose | 1.4 | 1.18 | 1.2 | 1.24 | 1.17 | 1.18 |
| math | 4.83 | 5.04 | 4.8 | 5.02 | 4.75 | 5.03 |
| reasoning | 2.22 | 2.99 | 2.8 | 2.58 | 2.66 | 2.55 |
| summary | 1.6 | 1.73 | 1.57 | 1.76 | 1.48 | 1.44 |
| structured | 6.29 | 6.48 | 6.6 | 6.23 | 6.35 | 6.61 |
| format | 5.82 | 5.82 | 6.14 | 5.91 | 5.96 | 6.02 |
| ceiling_count | 6.97 | 6.82 | 6.82 | 6.85 | 6.84 | 6.89 |

### Cold prefill (unique prefix)

| target | prompt tokens | TTFT (s) | prefill tok/s |
|---|---|---|---|
| 2000 | 2004 | 1.003 | 1998.3 |
| 8000 | 7919 | 4.649 | 1703.3 |
| 32000 | 31836 | 22.309 | 1427.0 |
| 64000 | 63764 | 52.701 | 1209.9 |
| 128000 | 127055 | 135.862 | 935.2 |
| 250000 | 248227 | 378.204 | 656.3 |
