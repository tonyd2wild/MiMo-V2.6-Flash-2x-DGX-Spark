## tp4-k4 (2026-09-22T14:12:09Z)

TP4 switch tp4-k4

Prompt set `v1` (identical across boots), temperature 0, thinking off. Tokens from the server's usage block; TTFT = first token delta.

### Throughput by concurrency (9 categories; the counting ceiling is excluded)

| C | aggregate tok/s | per-stream tok/s | mean TTFT (s) |
|---|---|---|---|
| C1 | 52.33 | 58.24 | 0.248 |
| C2 | 82.38 | 48.11 | 0.366 |
| C3 | 107.76 | 42.35 | 0.435 |
| C4 | 125.58 | 37.39 | 0.48 |
| C5 | 161.57 | 39.6 | 0.491 |
| C6 | 176.67 | 34.92 | 0.525 |

### Per-stream tok/s by category

| category | C1 | C2 | C3 | C4 | C5 | C6 |
|---|---|---|---|---|---|---|
| coding | 86.44 | 68.77 | 56.8 | 47.88 | 52.25 | 46.45 |
| json | 61.97 | 53.24 | 46.2 | 38.2 | 41.76 | 36.67 |
| narrative | 29.89 | 26.99 | 20.19 | 21.86 | 20.14 | 16.25 |
| prose | 27.55 | 24.16 | 24.56 | 25.01 | 22.53 | 18.95 |
| math | 82.45 | 52.08 | 56.21 | 50.92 | 49.53 | 44.75 |
| reasoning | 55.02 | 38.34 | 36.36 | 35.85 | 28.01 | 29.39 |
| summary | 31.68 | 30.29 | 25.35 | 24.3 | 24.11 | 19.77 |
| structured | 78.08 | 66.3 | 58.64 | 47.86 | 59.17 | 50.22 |
| format | 71.06 | 72.81 | 56.83 | 44.59 | 58.92 | 51.83 |
| ceiling_count | 84.08 | 77.82 | 66.32 | 68.39 | 59.22 | 44.6 |

### DFlash accepted tokens per draft step (7 drafted per step)

| category | C1 | C2 | C3 | C4 | C5 | C6 |
|---|---|---|---|---|---|---|
| coding | 3.6 | 3.35 | 3.44 | 3.49 | 3.55 | 3.6 |
| json | 2.2 | 2.52 | 2.48 | 2.56 | 2.5 | 2.41 |
| narrative | 0.83 | 0.71 | 0.82 | 0.79 | 0.74 | 0.74 |
| prose | 0.7 | 1.0 | 1.01 | 1.09 | 0.98 | 1.04 |
| math | 3.33 | 3.17 | 3.33 | 3.17 | 3.15 | 3.29 |
| reasoning | 1.97 | 1.99 | 1.93 | 2.0 | 2.08 | 2.04 |
| summary | 1.09 | 1.05 | 1.1 | 1.03 | 1.14 | 1.0 |
| structured | 3.81 | 3.83 | 3.84 | 3.76 | 3.84 | 3.84 |
| format | 3.54 | 3.52 | 3.63 | 3.57 | 3.59 | 3.53 |
| ceiling_count | 4.0 | 3.97 | 4.0 | 4.0 | 3.96 | 3.98 |

### Cold prefill (unique prefix)

| target | prompt tokens | TTFT (s) | prefill tok/s |
|---|---|---|---|
| 2000 | 2004 | 0.974 | 2057.5 |
| 8000 | 7919 | 2.707 | 2925.9 |
| 32000 | 31836 | 12.242 | 2600.5 |
| 64000 | 63764 | 29.625 | 2152.4 |
