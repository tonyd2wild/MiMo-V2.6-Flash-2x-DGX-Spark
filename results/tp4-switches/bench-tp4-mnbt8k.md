## tp4-mnbt8k (2026-09-22T14:33:06Z)

TP4 switch tp4-mnbt8k

Prompt set `v1` (identical across boots), temperature 0, thinking off. Tokens from the server's usage block; TTFT = first token delta.

### Throughput by concurrency (9 categories; the counting ceiling is excluded)

| C | aggregate tok/s | per-stream tok/s | mean TTFT (s) |
|---|---|---|---|
| C1 | 60.74 | 69.91 | 0.238 |
| C2 | 88.81 | 53.96 | 0.365 |
| C3 | 114.87 | 47.63 | 0.432 |
| C4 | 141.52 | 43.46 | 0.481 |
| C5 | 163.78 | 41.19 | 0.507 |
| C6 | 188.02 | 39.08 | 0.544 |

### Per-stream tok/s by category

| category | C1 | C2 | C3 | C4 | C5 | C6 |
|---|---|---|---|---|---|---|
| coding | 91.48 | 75.34 | 58.86 | 65.85 | 46.97 | 56.61 |
| json | 80.36 | 61.8 | 50.81 | 43.99 | 46.46 | 43.57 |
| narrative | 28.18 | 24.8 | 18.6 | 15.75 | 17.65 | 15.33 |
| prose | 27.4 | 25.99 | 20.58 | 22.47 | 20.34 | 18.24 |
| math | 98.17 | 66.12 | 64.81 | 61.29 | 54.84 | 41.14 |
| reasoning | 51.12 | 37.57 | 35.26 | 33.0 | 29.61 | 27.19 |
| summary | 35.61 | 26.24 | 23.04 | 21.0 | 16.88 | 17.81 |
| structured | 116.34 | 86.46 | 77.35 | 54.5 | 71.27 | 70.0 |
| format | 100.51 | 81.31 | 79.35 | 73.32 | 66.71 | 61.81 |
| ceiling_count | 136.79 | 102.72 | 92.34 | 77.84 | 83.89 | 73.61 |

### DFlash accepted tokens per draft step (7 drafted per step)

| category | C1 | C2 | C3 | C4 | C5 | C6 |
|---|---|---|---|---|---|---|
| coding | 4.61 | 5.16 | 4.57 | 5.46 | 5.34 | 5.31 |
| json | 3.8 | 3.71 | 3.55 | 3.82 | 3.59 | 3.72 |
| narrative | 0.68 | 0.8 | 0.75 | 0.8 | 0.81 | 0.74 |
| prose | 0.94 | 1.26 | 1.12 | 1.22 | 1.2 | 1.13 |
| math | 4.86 | 5.04 | 4.64 | 4.85 | 4.73 | 4.93 |
| reasoning | 2.14 | 2.18 | 2.21 | 2.46 | 2.34 | 2.31 |
| summary | 1.18 | 1.15 | 1.14 | 1.16 | 1.28 | 1.14 |
| structured | 6.21 | 6.52 | 6.09 | 6.29 | 6.36 | 6.08 |
| format | 4.9 | 5.38 | 5.86 | 5.51 | 5.58 | 5.59 |
| ceiling_count | 6.97 | 6.82 | 6.91 | 6.97 | 6.97 | 6.91 |

### Cold prefill (unique prefix)

| target | prompt tokens | TTFT (s) | prefill tok/s |
|---|---|---|---|
| 2000 | 2004 | 0.682 | 2937.9 |
| 8000 | 7919 | 3.821 | 2072.6 |
| 32000 | 31836 | 14.273 | 2230.5 |
| 64000 | 63764 | 27.323 | 2333.7 |
