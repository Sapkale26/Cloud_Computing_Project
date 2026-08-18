import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

procs = [1, 2, 4, 8, 16, 28]
times = [4.336, 8.298, 4.666, 4.538, 3.316, 3.583]
speedup = [times[0]/t for t in times]
efficiency = [s/p*100 for s,p in zip(speedup, procs)]

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle("MPI Monte Carlo Pi - Amdahls Law\nRaspberry Pi Cluster - Group 8 - Cloud Computing SS2026", fontsize=12, fontweight='bold')

axes[0].bar(range(len(procs)), times, color='steelblue', edgecolor='black')
axes[0].set_xticks(range(len(procs)))
axes[0].set_xticklabels([str(p) for p in procs])
axes[0].set_xlabel('MPI Processes')
axes[0].set_ylabel('Time [s]')
axes[0].set_title('Execution Time (avg 5 runs)')
for i, t in enumerate(times):
    axes[0].text(i, t+0.1, f'{t:.2f}s', ha='center', fontsize=8)

axes[1].plot(range(len(procs)), speedup, 'bo-', linewidth=2, markersize=6, label='Actual')
axes[1].plot(range(len(procs)), [p/1 for p in procs], 'r--', linewidth=1, label='Ideal')
axes[1].set_xticks(range(len(procs)))
axes[1].set_xticklabels([str(p) for p in procs])
axes[1].set_xlabel('MPI Processes')
axes[1].set_ylabel('Speedup')
axes[1].set_title("Speedup vs Ideal")
axes[1].legend()
for i, s in enumerate(speedup):
    axes[1].text(i, s+0.03, f'{s:.2f}x', ha='center', fontsize=8)

axes[2].bar(range(len(procs)), efficiency, color='darkorange', edgecolor='black')
axes[2].set_xticks(range(len(procs)))
axes[2].set_xticklabels([str(p) for p in procs])
axes[2].set_xlabel('MPI Processes')
axes[2].set_ylabel('Efficiency [%]')
axes[2].set_title('Parallel Efficiency')
for i, e in enumerate(efficiency):
    axes[2].text(i, e+1, f'{e:.1f}%', ha='center', fontsize=8)

plt.tight_layout()
plt.savefig('/home/pi/cluster/benchmarks/mpi/mpi_results.png', dpi=150, bbox_inches='tight')
print("Saved!")
