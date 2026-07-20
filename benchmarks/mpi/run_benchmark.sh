#!/bin/bash
# ============================================================
# MPI Monte Carlo Pi Benchmark
# Demonstrates Amdahl's & Gustafson's Law
# Run on Pi 5: bash benchmarks/mpi/run_benchmark.sh
# ============================================================

HOSTFILE="$HOME/cluster/benchmarks/mpi/hostfile"
BINARY="$HOME/cluster/benchmarks/mpi/pi_mpi"
RESULTS="$HOME/cluster/benchmarks/mpi/results_$(date +%Y%m%d_%H%M%S).txt"
RUNS=5  # Number of runs per config for statistical accuracy

# Compile
echo "Compiling pi_mpi.c..."
mpicc "$HOME/cluster/benchmarks/mpi/pi_mpi.c" -o "$BINARY"

echo "=== MPI Monte Carlo Pi Benchmark ===" | tee "$RESULTS"
echo "Date: $(date)" | tee -a "$RESULTS"
echo "Runs per config: $RUNS" | tee -a "$RESULTS"
echo "" | tee -a "$RESULTS"

for np in 1 2 4 8 16 28; do
    echo "--- np=$np ---" | tee -a "$RESULTS"
    times=()
    for run in $(seq 1 $RUNS); do
        result=$({ time mpirun \
            --hostfile "$HOSTFILE" \
            --map-by node \
            -np $np \
            "$BINARY" 2>/dev/null; } 2>&1)

        pi_val=$(echo "$result" | grep "PI calculated" | awk '{print $NF}')
        time_str=$(echo "$result" | grep "real" | awk '{print $2}')
        # Convert time to seconds
        time_sec=$(echo "$time_str" | sed 's/m/\*60+/;s/s//' | bc 2>/dev/null || echo "0")
        times+=("$time_sec")
        echo "  Run $run: PI=$pi_val  Time=${time_str}" | tee -a "$RESULTS"
    done
    echo "" | tee -a "$RESULTS"
done

echo "=== DONE ===" | tee -a "$RESULTS"
echo "Results saved to: $RESULTS"

# Generate Python plot
python3 - << 'PYEOF'
import re, sys

results_file = sorted(__import__('glob').glob('/root/cluster/benchmarks/mpi/results_*.txt'))[-1]
print(f"Analyzing: {results_file}")

data = {}
with open(results_file) as f:
    current_np = None
    for line in f:
        m = re.match(r'--- np=(\d+) ---', line)
        if m:
            current_np = int(m.group(1))
            data[current_np] = []
        if current_np and 'Time=' in line:
            m2 = re.search(r'Time=(\d+)m([\d.]+)s', line)
            if m2:
                t = int(m2.group(1)) * 60 + float(m2.group(2))
                data[current_np].append(t)

print("\n=== Results Summary ===")
print(f"{'Processes':>10} {'Avg Time':>10} {'Speedup':>10} {'Efficiency':>12}")
t1 = sum(data[1]) / len(data[1]) if 1 in data else None
for np, times in sorted(data.items()):
    avg = sum(times) / len(times)
    speedup = t1 / avg if t1 else 1.0
    efficiency = speedup / np * 100
    print(f"{np:>10} {avg:>10.3f}s {speedup:>10.2f}x {efficiency:>11.1f}%")
PYEOF
