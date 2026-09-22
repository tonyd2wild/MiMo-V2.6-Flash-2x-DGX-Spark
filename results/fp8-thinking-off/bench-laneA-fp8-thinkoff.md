## laneA-fp8-thinkoff (2026-09-22T02:34:38Z)

Lane A fp8 KV GMU 0.90 300K, server default enable_thinking=false, stock drafter

Prompt set `v1` (identical across boots), temperature 0, thinking off. Tokens from the server's usage block; TTFT = first token delta.

### Throughput by concurrency (9 categories; the counting ceiling is excluded)

| C | aggregate tok/s | per-stream tok/s | mean TTFT (s) |
|---|---|---|---|
| C1 | 44.52 | 52.42 | 0.398 |
| C2 | 71.4 | 42.23 | 0.385 |
| C3 | 97.87 | 38.24 | 0.458 |
| C4 | 116.96 | 34.87 | 0.439 |
| C5 | 137.63 | 32.63 | 0.468 |
| C6 | 152.65 | 30.5 | 0.5 |

### Per-stream tok/s by category

| category | C1 | C2 | C3 | C4 | C5 | C6 |
|---|---|---|---|---|---|---|
| coding | 69.15 | 48.52 | 49.75 | 46.25 | 40.23 | 37.63 |
| json | 52.78 | 40.52 | 40.81 | 31.77 | 35.62 | 31.78 |
| narrative | 23.04 | 17.1 | 13.77 | 13.27 | 12.28 | 11.21 |
| prose | 26.22 | 20.23 | 16.73 | 16.79 | 14.3 | 13.19 |
| math | 65.92 | 65.97 | 51.03 | 45.12 | 41.46 | 40.5 |
| reasoning | 35.88 | 29.54 | 25.37 | 24.58 | 23.99 | 22.62 |
| summary | 28.83 | 21.06 | 18.91 | 17.14 | 15.96 | 15.6 |
| structured | 79.33 | 62.1 | 58.44 | 54.42 | 52.72 | 50.81 |
| format | 90.65 | 75.07 | 69.38 | 64.45 | 57.09 | 51.15 |
| ceiling_count | 88.75 | 73.21 | 65.49 | 61.1 | 61.67 | 54.66 |

### DFlash accepted tokens per draft step (7 drafted per step)

| category | C1 | C2 | C3 | C4 | C5 | C6 |
|---|---|---|---|---|---|---|
| coding | 5.13 | 5.16 | 5.01 | 5.33 | 5.16 | 5.16 |
| json | 3.57 | 3.76 | 3.92 | 3.42 | 3.75 | 3.54 |
| narrative | 0.96 | 0.83 | 0.74 | 0.79 | 0.81 | 0.76 |
| prose | 1.33 | 1.26 | 1.13 | 1.42 | 1.15 | 1.17 |
| math | 5.5 | 5.26 | 5.02 | 5.08 | 4.99 | 4.86 |
| reasoning | 2.79 | 2.4 | 2.33 | 2.56 | 2.71 | 2.7 |
| summary | 1.57 | 1.37 | 1.6 | 1.6 | 1.59 | 1.64 |
| structured | 6.21 | 6.25 | 6.41 | 6.25 | 6.38 | 6.41 |
| format | 6.73 | 6.0 | 6.06 | 6.2 | 5.92 | 6.02 |
| ceiling_count | 6.82 | 6.89 | 6.86 | 6.89 | 6.82 | 6.84 |

### Cold prefill (unique prefix)

| target | prompt tokens | TTFT (s) | prefill tok/s |
|---|---|---|---|
| 2000 | 2004 | 1.028 | 1949.9 |
| 8000 | 7919 | 4.645 | 1704.8 |
| 32000 | 31836 | 22.884 | 1391.2 |
| 64000 | 63764 | 53.1 | 1200.8 |
| 128000 | 127055 | 140.853 | 902.0 |
| 250000 | 248227 | 391.799 | 633.6 |
