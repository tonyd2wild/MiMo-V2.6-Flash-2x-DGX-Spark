## tp4-gmu85-hiconc (2026-09-22T13:47:30Z)

TP4 high concurrency

Prompt set `v1` (identical across boots), temperature 0, thinking off. Tokens from the server's usage block; TTFT = first token delta.

### Throughput by concurrency (9 categories; the counting ceiling is excluded)

| C | aggregate tok/s | per-stream tok/s | mean TTFT (s) |
|---|---|---|---|
| C8 | 220.5 | 33.82 | 0.565 |
| C12 | 251.82 | 25.31 | 0.658 |
| C16 | 268.97 | 20.58 | 0.775 |
| C24 | 363.22 | 18.3 | 0.936 |
| C32 | 397.46 | 15.19 | 1.21 |

### Per-stream tok/s by category

| category | C8 | C12 | C16 | C24 | C32 |
|---|---|---|---|---|---|
| coding | 43.67 | 33.43 | 25.6 | 24.25 | 19.06 |
| json | 37.92 | 26.81 | 20.58 | 20.5 | 16.94 |
| narrative | 12.32 | 9.21 | 8.22 | 7.31 | 5.67 |
| prose | 15.14 | 11.84 | 9.62 | 8.66 | 7.11 |
| math | 46.13 | 33.68 | 27.43 | 24.51 | 20.63 |
| reasoning | 23.92 | 17.15 | 14.9 | 12.37 | 11.26 |
| summary | 13.98 | 11.73 | 9.6 | 8.89 | 6.86 |
| structured | 58.3 | 42.51 | 34.94 | 29.99 | 24.7 |
| format | 52.97 | 41.4 | 34.37 | 28.23 | 24.45 |
| ceiling_count | 64.63 | 47.07 | 38.42 | 33.05 | 26.27 |

### DFlash accepted tokens per draft step (7 drafted per step)

| category | C8 | C12 | C16 | C24 | C32 |
|---|---|---|---|---|---|
| coding | 5.01 | 5.07 | 5.28 | 5.31 | 5.04 |
| json | 3.6 | 3.47 | 3.51 | 3.51 | 3.64 |
| narrative | 0.75 | 0.72 | 0.74 | 0.74 | 0.72 |
| prose | 1.06 | 1.13 | 1.19 | 1.13 | 1.15 |
| math | 4.97 | 4.78 | 4.76 | 4.73 | 4.88 |
| reasoning | 2.31 | 2.27 | 2.31 | 2.28 | 2.37 |
| summary | 1.23 | 1.27 | 1.22 | 1.26 | 1.21 |
| structured | 6.26 | 6.18 | 6.18 | 6.37 | 6.28 |
| format | 5.5 | 5.71 | 5.69 | 5.56 | 5.68 |
| ceiling_count | 6.94 | 6.85 | 6.9 | 6.83 | 6.84 |

### Cold prefill (unique prefix)

| target | prompt tokens | TTFT (s) | prefill tok/s |
|---|---|---|---|
