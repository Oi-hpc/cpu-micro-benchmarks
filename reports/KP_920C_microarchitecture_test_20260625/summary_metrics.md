# Summary Metrics

- ASIMD SP FMLA avg: 27.86 FLOPs/cycle
- SVE SP FMLA avg: 31.87 FLOPs/cycle
- SVE/ASIMD SP ratio: 1.14x
- ASIMD DP FMLA avg: 14.02 FLOPs/cycle
- SVE DP FMLA avg: 15.95 FLOPs/cycle
- SVE/ASIMD DP ratio: 1.14x

## Instruction Latency
- fp_fmadd_single: latency 2.00/4.00 cycles, throughput 3.94 instr/cycle
- fp_fmadd_double: latency 2.00/4.00 cycles, throughput 3.94 instr/cycle
- asimd_fp_fmla_single: latency 2.00/4.00 cycles, throughput inf instr/cycle
- asimd_fp_fadd_single: latency 2.00 cycles, throughput 3.95 instr/cycle
- asimd_fp_fmul_single: latency 3.00 cycles, throughput 3.94 instr/cycle
- asimd_fp_fadd_double: latency 2.00 cycles, throughput 3.95 instr/cycle
- asimd_fp_fmul_double: latency 3.00 cycles, throughput 3.94 instr/cycle

## Coverage
- register_file_size rows: 5607
- sched_size rows: 7826
- rob_size rows: 1024
- memory_latency rows: 66
- dtlb_size rows: 4096
- fetch_bandwidth rows: 43
