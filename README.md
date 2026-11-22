% Monte Carlo Python Benchmarks

This is a repo to show naive and more optimized python implementations of the MCTS.

## Experiments

- Done in Linux (Fedora) with Python 3.14.2. 
- Peak Memory done with trace_malloc (`-m`) in MiB.
- CPU done with process_time (`-p`) with min/median/mean in seconds over 5 iterations.
- Seed 55948825, 200000 iterations

| Program       | min/median/mean time | Peak Memory | Description |
| ------------- | -------------------  | ----------- | ----------- |
| mcts_naive.py | 8.636/31.100/30.299  |             |             |

