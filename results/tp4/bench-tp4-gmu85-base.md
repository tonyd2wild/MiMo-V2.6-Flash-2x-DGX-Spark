## tp4-gmu85-base (2026-09-22T13:41:40Z)

TP4 across 4 Sparks: fp8 KV, GMU 0.85, max-model-len 500000, max-num-seqs 32, DFlash 7, marlin, async off, thinking off

Prompt set `v1` (identical across boots), temperature 0, thinking off. Tokens from the server's usage block; TTFT = first token delta.

### Throughput by concurrency (9 categories; the counting ceiling is excluded)

| C | aggregate tok/s | per-stream tok/s | mean TTFT (s) |
|---|---|---|---|
| C1 | 61.27 | 70.66 | 0.235 |
| C2 | 82.3 | 49.91 | 0.354 |
| C3 | 109.1 | 43.81 | 0.437 |
| C4 | 144.56 | 44.46 | 0.487 |
| C5 | 168.36 | 42.02 | 0.511 |
| C6 | 191.64 | 39.41 | 0.551 |

### Per-stream tok/s by category

| category | C1 | C2 | C3 | C4 | C5 | C6 |
|---|---|---|---|---|---|---|
| coding | 92.29 | 57.97 | 68.32 | 51.78 | 57.84 | 55.18 |
| json | 76.58 | 44.23 | 41.5 | 47.58 | 48.29 | 43.46 |
| narrative | 23.88 | 17.87 | 20.1 | 19.28 | 16.61 | 14.44 |
| prose | 28.48 | 9.4 | 24.09 | 22.37 | 18.7 | 17.96 |
| math | 102.81 | 82.32 | 65.55 | 63.28 | 50.24 | 56.27 |
| reasoning | 50.83 | 38.55 | 35.04 | 34.22 | 29.78 | 27.76 |
| summary | 34.58 | 26.7 | 24.44 | 19.41 | 19.74 | 17.67 |
| structured | 116.81 | 86.75 | 60.76 | 71.73 | 70.98 | 56.75 |
| format | 109.66 | 85.36 | 54.48 | 70.45 | 66.04 | 65.24 |
| ceiling_count | 109.24 | 103.64 | 68.34 | 84.95 | 79.6 | 75.04 |

### DFlash accepted tokens per draft step (7 drafted per step)

| category | C1 | C2 | C3 | C4 | C5 | C6 |
|---|---|---|---|---|---|---|
| coding | 4.56 | 4.61 | 5.39 | 5.15 | 5.31 | 5.27 |
| json | 3.62 | 3.01 | 3.48 | 3.77 | 3.72 | 3.5 |
| narrative | 0.64 | 1.1 | 0.82 | 0.8 | 0.76 | 0.75 |
| prose | 1.0 | 1.25 | 1.11 | 1.18 | 1.08 | 1.1 |
| math | 5.3 | 5.0 | 4.78 | 4.82 | 4.78 | 5.03 |
| reasoning | 2.11 | 2.11 | 2.23 | 2.47 | 2.31 | 2.32 |
| summary | 1.22 | 1.14 | 1.24 | 1.27 | 1.18 | 1.25 |
| structured | 6.21 | 6.52 | 6.24 | 6.2 | 6.35 | 6.35 |
| format | 5.5 | 5.71 | 5.75 | 5.67 | 5.43 | 5.65 |
| ceiling_count | 6.74 | 6.82 | 6.91 | 6.92 | 6.93 | 6.94 |

### Cold prefill (unique prefix)

| target | prompt tokens | TTFT (s) | prefill tok/s |
|---|---|---|---|
| 2000 | 2004 | 0.679 | 2952.1 |
| 8000 | 7919 | 2.72 | 2911.4 |
| 32000 | 31836 | 12.229 | 2603.3 |
| 64000 | 63764 | 29.359 | 2171.9 |
