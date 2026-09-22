## tp4-gmu85-c1clean (2026-09-22T13:56:08Z)

TP4 quiet-lane C1 rerun

Prompt set `v1` (identical across boots), temperature 0, thinking off. Tokens from the server's usage block; TTFT = first token delta.

### Throughput by concurrency (9 categories; the counting ceiling is excluded)

| C | aggregate tok/s | per-stream tok/s | mean TTFT (s) |
|---|---|---|---|
| C1 | 59.82 | 68.81 | 0.228 |

### Per-stream tok/s by category

| category | C1 |
|---|---|
| coding | 83.17 |
| json | 75.27 |
| narrative | 29.85 |
| prose | 34.88 |
| math | 95.4 |
| reasoning | 45.5 |
| summary | 31.95 |
| structured | 114.92 |
| format | 108.32 |
| ceiling_count | 136.16 |

### DFlash accepted tokens per draft step (7 drafted per step)

| category | C1 |
|---|---|
| coding | 5.0 |
| json | 3.62 |
| narrative | 0.75 |
| prose | 1.11 |
| math | 4.83 |
| reasoning | 2.43 |
| summary | 1.08 |
| structured | 6.21 |
| format | 5.56 |
| ceiling_count | 6.97 |

### Cold prefill (unique prefix)

| target | prompt tokens | TTFT (s) | prefill tok/s |
|---|---|---|---|
