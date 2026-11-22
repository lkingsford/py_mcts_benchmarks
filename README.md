% Monte Carlo Python Benchmarks

This is a repo to show naive and more optimized python implementations of the MCTS.

## Notes
- Running `-m` and `-p` together distorts process_time really significantly.

## Experiments

- Done in Linux (Fedora) with Python 3.14.2. 
- Peak Memory done with trace_malloc (`-m`) in MiB.
- CPU done with process_time (`-p`) with min/median/mean in seconds over 5 iterations.
- Seed 55948825, 200000 iterations.

| Program             | min/median/mean time | Peak Memory | 
| ------------------- | -------------------  | ----------- |
| 0_mcts_naive.py     | 23.728/26.312/25.556 | 275.16      |
| 1_lazy_expansion.py | 2.870/3.027/3.009    | 17.80       |

