"""
benchmark_graphs.py
Generate all benchmark graphs for Group 8 Cloud Computing SS2026
Run: python3 benchmark_graphs.py
Output: graphs saved to ~/cluster/benchmarks/graphs/
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import os

OUTPUT_DIR = os.path.expanduser('~/cluster/benchmarks/graphs')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Colors ────────────────────────────────────────────────
BLUE = '#2a78d6'
GREEN = '#1baf7a'
RED = '#e63946'
ORANGE = '#f4a261'
PURPLE = '#7b2d8b'
GRAY = '#aaaaaa'

def save(name):
    path = f'{OUTPUT_DIR}/{name}.png'
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Saved: {path}')

# ══════════════════════════════════════════════════════════
# GRAPH 1: MPI Monte Carlo Pi — Amdahl's Law
# ══════════════════════════════════════════════════════════
procs    = [1, 2, 4, 8, 16, 28]
times    = [4.336, 8.298, 4.666, 4.538, 3.316, 3.583]
speedup  = [times[0]/t for t in times]
efficiency = [s/p*100 for s,p in zip(speedup, procs)]
ideal_sp = [p for p in procs]

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle("MPI Monte Carlo Pi — Amdahl's Law\n"
             "Raspberry Pi Cluster — Group 8 — Cloud Computing SS2026",
             fontsize=13, fontweight='bold')

# Time
ax = axes[0]
bars = ax.bar(range(len(procs)), times, color=[RED if t==max(times) else BLUE for t in times],
              edgecolor='white', linewidth=0.5, width=0.6)
ax.set_xticks(range(len(procs)))
ax.set_xticklabels([str(p) for p in procs])
ax.set_xlabel('MPI Processes', fontsize=11)
ax.set_ylabel('Time [s]', fontsize=11)
ax.set_title('Execution Time (avg 5 runs, 100M points)', fontsize=10)
for i, t in enumerate(times):
    ax.text(i, t+0.1, f'{t:.2f}s', ha='center', fontsize=8, fontweight='bold')
ax.axhline(y=times[0], color=GRAY, linestyle='--', alpha=0.5, label='np=1 baseline')
ax.legend(fontsize=8)

# Speedup
ax = axes[1]
ax.plot(range(len(procs)), speedup, 'o-', color=BLUE, linewidth=2.5,
        markersize=7, label='Actual speedup', zorder=3)
ax.plot(range(len(procs)), [p/procs[0] for p in procs], '--',
        color=GRAY, linewidth=1.5, label='Ideal (linear)', zorder=2)
ax.axhline(y=1, color=RED, linestyle=':', alpha=0.5, label='Baseline (1.0x)')
ax.fill_between(range(len(procs)), speedup, [p/procs[0] for p in procs],
                alpha=0.1, color=RED, label='Lost performance')
ax.set_xticks(range(len(procs)))
ax.set_xticklabels([str(p) for p in procs])
ax.set_xlabel('MPI Processes', fontsize=11)
ax.set_ylabel('Speedup', fontsize=11)
ax.set_title("Speedup vs Ideal (Amdahl's Law)", fontsize=10)
ax.legend(fontsize=8)
for i, s in enumerate(speedup):
    ax.annotate(f'{s:.2f}x', (i, s), textcoords='offset points',
                xytext=(0, 8), ha='center', fontsize=8, fontweight='bold')

# Efficiency
ax = axes[2]
bars = ax.bar(range(len(procs)), efficiency,
              color=[GREEN if e > 50 else ORANGE if e > 20 else RED for e in efficiency],
              edgecolor='white', linewidth=0.5, width=0.6)
ax.axhline(y=100, color=GRAY, linestyle='--', alpha=0.5, label='100% efficient')
ax.axhline(y=50, color=ORANGE, linestyle=':', alpha=0.5, label='50% threshold')
ax.set_xticks(range(len(procs)))
ax.set_xticklabels([str(p) for p in procs])
ax.set_xlabel('MPI Processes', fontsize=11)
ax.set_ylabel('Efficiency [%]', fontsize=11)
ax.set_title('Parallel Efficiency', fontsize=10)
ax.legend(fontsize=8)
for i, e in enumerate(efficiency):
    ax.text(i, e+1, f'{e:.1f}%', ha='center', fontsize=8, fontweight='bold')

plt.tight_layout()
save('mpi_amdahl')

# ══════════════════════════════════════════════════════════
# GRAPH 2: MPI Gustafson's Law
# ══════════════════════════════════════════════════════════
procs_g  = [1, 2, 4, 8, 16, 28]
points_g = [100, 200, 400, 800, 1600, 2800]  # in millions
times_g  = [1.605, 8.276, 8.277, 12.700, 14.451, 16.957]
work_g   = [p/points_g[0] for p in points_g]
time_ratio = [t/times_g[0] for t in times_g]
gust_sp  = [w/r for w,r in zip(work_g, time_ratio)]

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle("MPI Monte Carlo Pi — Gustafson's Law (Weak Scaling)\n"
             "Problem size scales with number of processors",
             fontsize=13, fontweight='bold')

ax = axes[0]
ax2 = ax.twinx()
bars = ax.bar(range(len(procs_g)), times_g, color=GREEN, alpha=0.7,
              edgecolor='white', width=0.4, label='Time [s]')
line = ax2.plot(range(len(procs_g)), points_g, 'rs--', linewidth=2,
                markersize=7, label='Problem size (M points)')
ax.set_xticks(range(len(procs_g)))
ax.set_xticklabels([str(p) for p in procs_g])
ax.set_xlabel('MPI Processes', fontsize=11)
ax.set_ylabel('Time [s]', fontsize=11, color=GREEN)
ax2.set_ylabel('Problem Size [M points]', fontsize=11, color=RED)
ax.set_title('Weak Scaling: Time vs Problem Size', fontsize=10)
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2, fontsize=8)

ax = axes[1]
ax.plot(range(len(procs_g)), gust_sp, 'o-', color=PURPLE, linewidth=2.5,
        markersize=7, label='Gustafson speedup', zorder=3)
ax.plot(range(len(procs_g)), [1]*len(procs_g), '--',
        color=GRAY, linewidth=1.5, label='Baseline (1.0x)')
ax.fill_between(range(len(procs_g)), gust_sp, [1]*len(procs_g),
                alpha=0.2, color=PURPLE)
ax.set_xticks(range(len(procs_g)))
ax.set_xticklabels([str(p) for p in procs_g])
ax.set_xlabel('MPI Processes', fontsize=11)
ax.set_ylabel('Gustafson Speedup', fontsize=11)
ax.set_title("Gustafson's Law: Work done relative to np=1", fontsize=10)
ax.legend(fontsize=8)
for i, s in enumerate(gust_sp):
    ax.annotate(f'{s:.2f}x', (i, s), textcoords='offset points',
                xytext=(0, 8), ha='center', fontsize=8)

plt.tight_layout()
save('mpi_gustafson')

# ══════════════════════════════════════════════════════════
# GRAPH 3: HPL Benchmark
# ══════════════════════════════════════════════════════════
procs_h  = [1, 2, 4, 8, 16]
gflops   = [12.988, 2.192, 1.543, 1.092, 0.586]
times_h  = [17.61, 104.37, 148.27, 209.40, 390.48]
sp_h     = [gflops[0]/g for g in gflops]  # inverse - more is faster

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle("HPL/LINPACK Benchmark — Heterogeneous Cluster\n"
             "N=7000, NB=64 | Pi 5 + Pi 3 workers",
             fontsize=13, fontweight='bold')

ax = axes[0]
colors_h = [BLUE] + [RED]*4  # Pi5 alone is blue, others red
bars = ax.bar(range(len(procs_h)), gflops, color=colors_h,
              edgecolor='white', linewidth=0.5, width=0.6)
ax.set_xticks(range(len(procs_h)))
ax.set_xticklabels([str(p) for p in procs_h])
ax.set_xlabel('MPI Processes', fontsize=11)
ax.set_ylabel('Performance [GFlops]', fontsize=11)
ax.set_title('HPL Performance vs Processes (PASSED)', fontsize=10)
for i, g in enumerate(gflops):
    ax.text(i, g+0.1, f'{g:.3f}', ha='center', fontsize=9, fontweight='bold')
ax.legend(handles=[
    plt.Rectangle((0,0),1,1, color=BLUE, label='Pi 5 alone (best)'),
    plt.Rectangle((0,0),1,1, color=RED, label='Pi 5 + Pi 3 workers')
], fontsize=9)

ax = axes[1]
ax.plot(range(len(procs_h)), times_h, 'o-', color=RED, linewidth=2.5,
        markersize=7, label='Execution time')
ax.fill_between(range(len(procs_h)), times_h, min(times_h),
                alpha=0.2, color=RED)
ax.set_xticks(range(len(procs_h)))
ax.set_xticklabels([str(p) for p in procs_h])
ax.set_xlabel('MPI Processes', fontsize=11)
ax.set_ylabel('Time [s]', fontsize=11)
ax.set_title('Execution Time Increases with More Nodes', fontsize=10)
ax.legend(fontsize=9)
for i, t in enumerate(times_h):
    ax.annotate(f'{t:.0f}s', (i, t), textcoords='offset points',
                xytext=(0, 8), ha='center', fontsize=9)

plt.tight_layout()
save('hpl_benchmark')

# ══════════════════════════════════════════════════════════
# GRAPH 4: Task Distributor — Amdahl's Law
# ══════════════════════════════════════════════════════════
nodes_td = [1, 2, 4, 7]
times_td = [5.166, 7.534, 6.675, 9.995]
par_td   = [5.020, 7.030, 6.033, 9.060]
seq1_td  = [0.018, 0.030, 0.016, 0.016]
seq2_td  = [0.106, 0.453, 0.606, 0.902]
sp_td    = [times_td[0]/t for t in times_td]

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle("Task Distributor — Amdahl's Law (Fixed 800×600 Image)\n"
             "Non-MPI parallel rendering with POV-Ray",
             fontsize=13, fontweight='bold')

ax = axes[0]
x = np.arange(len(nodes_td))
w = 0.5
p1 = ax.bar(x, seq1_td, w, label='Sequential part 1', color=RED)
p2 = ax.bar(x, par_td, w, bottom=seq1_td, label='Parallel part (POV-Ray)', color=GREEN)
p3 = ax.bar(x, seq2_td, w,
            bottom=[s+p for s,p in zip(seq1_td, par_td)],
            label='Sequential part 2 (image assembly)', color=ORANGE)
ax.set_xticks(x)
ax.set_xticklabels([str(n) for n in nodes_td])
ax.set_xlabel('Worker Nodes', fontsize=11)
ax.set_ylabel('Time [s]', fontsize=11)
ax.set_title('Stacked Time: Sequential vs Parallel', fontsize=10)
ax.legend(fontsize=8)

ax = axes[1]
ax.plot(range(len(nodes_td)), sp_td, 'o-', color=BLUE, linewidth=2.5,
        markersize=8, label='Actual speedup', zorder=3)
ax.axhline(y=1, color=GRAY, linestyle='--', alpha=0.7, label='Baseline (1.0x)')
ax.fill_between(range(len(nodes_td)), sp_td, [1]*len(nodes_td),
                alpha=0.2, color=RED, label='Performance loss')
ax.set_xticks(range(len(nodes_td)))
ax.set_xticklabels([str(n) for n in nodes_td])
ax.set_xlabel('Worker Nodes', fontsize=11)
ax.set_ylabel('Speedup', fontsize=11)
ax.set_title("Speedup — Communication Overhead Dominates", fontsize=10)
ax.legend(fontsize=8)
for i, s in enumerate(sp_td):
    ax.annotate(f'{s:.2f}x', (i, s), textcoords='offset points',
                xytext=(0, 8), ha='center', fontsize=9, fontweight='bold')

plt.tight_layout()
save('task_distributor_amdahl')

# ══════════════════════════════════════════════════════════
# GRAPH 5: Task Distributor — Gustafson's Law
# ══════════════════════════════════════════════════════════
nodes_g2  = [1, 2, 4, 7]
sizes_g2  = ['320×240', '640×480', '1280×960', '2240×1680']
pixels_g2 = [320*240, 640*480, 1280*960, 2240*1680]
times_g2  = [4.162, 4.370, 6.825, 19.730]
px_per_s  = [p/t for p,t in zip(pixels_g2, times_g2)]
gust_eff  = [px/pixels_g2[0] / (t/times_g2[0]) for px,t in zip(pixels_g2, times_g2)]

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle("Task Distributor — Gustafson's Law (Scaled Image Size)\n"
             "Problem size scales with number of workers",
             fontsize=13, fontweight='bold')

ax = axes[0]
ax2 = ax.twinx()
bars = ax.bar(range(len(nodes_g2)), times_g2, color=PURPLE, alpha=0.7,
              edgecolor='white', width=0.4, label='Time [s]')
line = ax2.plot(range(len(nodes_g2)), [p/1000000 for p in pixels_g2],
                'rs--', linewidth=2, markersize=7, label='Megapixels')
ax.set_xticks(range(len(nodes_g2)))
ax.set_xticklabels([f'{n}\n{s}' for n,s in zip(nodes_g2, sizes_g2)], fontsize=8)
ax.set_xlabel('Worker Nodes / Image Size', fontsize=11)
ax.set_ylabel('Time [s]', fontsize=11, color=PURPLE)
ax2.set_ylabel('Image Size [Megapixels]', fontsize=11, color=RED)
ax.set_title('Weak Scaling: More Workers = Bigger Image', fontsize=10)
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1+lines2, labels1+labels2, fontsize=8)

ax = axes[1]
ax.bar(range(len(nodes_g2)), [p/1000 for p in px_per_s],
       color=[GREEN if p > px_per_s[0] else RED for p in px_per_s],
       edgecolor='white', width=0.6)
ax.set_xticks(range(len(nodes_g2)))
ax.set_xticklabels([f'{n}\n{s}' for n,s in zip(nodes_g2, sizes_g2)], fontsize=8)
ax.set_xlabel('Worker Nodes / Image Size', fontsize=11)
ax.set_ylabel('Throughput [K pixels/s]', fontsize=11)
ax.set_title("Pixel Throughput — Gustafson's Scaling", fontsize=10)
for i, p in enumerate(px_per_s):
    ax.text(i, p/1000+0.5, f'{p/1000:.1f}K', ha='center', fontsize=9, fontweight='bold')

plt.tight_layout()
save('task_distributor_gustafson')

# ══════════════════════════════════════════════════════════
# GRAPH 6: Combined Comparison — All Laws
# ══════════════════════════════════════════════════════════
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Amdahl's & Gustafson's Law — Complete Summary\n"
             "Group 8 — Raspberry Pi Cluster — Cloud Computing SS2026",
             fontsize=14, fontweight='bold')

# MPI Speedup
ax = axes[0, 0]
ax.plot(range(len(procs)), speedup, 'o-', color=BLUE, linewidth=2.5,
        markersize=7, label='MPI Monte Carlo (Amdahl)')
ax.plot(range(len(procs)), [p/procs[0] for p in procs], '--',
        color=GRAY, linewidth=1.5, label='Ideal linear')
ax.set_xticks(range(len(procs)))
ax.set_xticklabels([str(p) for p in procs])
ax.set_xlabel('Processes')
ax.set_ylabel('Speedup')
ax.set_title("Amdahl's Law — MPI (Strong Scaling)")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# HPL GFlops
ax = axes[0, 1]
ax.bar(range(len(procs_h)), gflops,
       color=[BLUE]+[RED]*4, edgecolor='white', width=0.6)
ax.set_xticks(range(len(procs_h)))
ax.set_xticklabels([str(p) for p in procs_h])
ax.set_xlabel('Processes')
ax.set_ylabel('GFlops')
ax.set_title("Amdahl's Law — HPL (Heterogeneous Cluster)")
ax.grid(True, alpha=0.3, axis='y')

# Task Distributor Amdahl
ax = axes[1, 0]
ax.plot(range(len(nodes_td)), sp_td, 's-', color=ORANGE, linewidth=2.5,
        markersize=7, label='Task Distributor (Amdahl)')
ax.axhline(y=1, color=GRAY, linestyle='--', linewidth=1.5)
ax.set_xticks(range(len(nodes_td)))
ax.set_xticklabels([str(n) for n in nodes_td])
ax.set_xlabel('Worker Nodes')
ax.set_ylabel('Speedup')
ax.set_title("Amdahl's Law — Task Distributor (Fixed Image)")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# Gustafson comparison
ax = axes[1, 1]
ax.plot(range(len(procs_g)), gust_sp, 'D-', color=GREEN, linewidth=2.5,
        markersize=7, label='MPI Monte Carlo (Gustafson)')
ax.plot(range(len(nodes_g2)), gust_eff, '^-', color=PURPLE, linewidth=2.5,
        markersize=7, label='Task Distributor (Gustafson)')
ax.axhline(y=1, color=GRAY, linestyle='--', linewidth=1.5, label='Baseline')
ax.set_xticks(range(max(len(procs_g), len(nodes_g2))))
ax.set_xlabel('Nodes / Processes')
ax.set_ylabel("Gustafson's Speedup")
ax.set_title("Gustafson's Law — Weak Scaling Comparison")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

plt.tight_layout()
save('combined_laws_summary')

print(f'\n✅ All graphs saved to {OUTPUT_DIR}')
print('Files:')
for f in os.listdir(OUTPUT_DIR):
    print(f'  {f}')
