# Benchmark Conclusions — Group 8
## Cloud Computing SS2026 | Frankfurt University of Applied Sciences
## Prof. Dr. Christian Baun

---

## Task 3 — MPI Benchmarks

### MPI Monte Carlo Pi — Amdahl's Law (Strong Scaling)

**Configuration:** Fixed 100M points, 5 runs each, np = 1, 2, 4, 8, 16, 28

| Processes | Avg Time (s) | Speedup | Efficiency |
|-----------|-------------|---------|------------|
| 1 | 4.336 | 1.00x | 100.0% |
| 2 | 8.298 | 0.52x | 26.0% |
| 4 | 4.666 | 0.93x | 23.2% |
| 8 | 4.538 | 0.96x | 11.9% |
| 16 | 3.316 | 1.31x | 8.2% |
| 28 | 3.583 | 1.21x | 4.3% |

**Key Observations:**
- np=2 is **49% SLOWER** than np=1 — SSH connection setup overhead dominates
- np=16 is the sweet spot — best speedup of **1.31x**
- np=28 slightly slower than np=16 — too much MPI communication overhead
- Estimated serial fraction: **~44%** (SSH + MPI_Reduce overhead)

**Conclusion:**
Amdahl's Law is clearly demonstrated. With a serial fraction of ~44%, the maximum theoretical speedup is 1/(0.44) = **2.27x**, which explains why we cannot exceed this even with 28 processes. The serial fraction comes from SSH connection establishment (~0.5s per node) and the MPI_Reduce collective operation. The Pi 5 (Cortex-A76, 2.4GHz) is significantly faster than Pi 3 workers (Cortex-A53, 1.2GHz), so adding Pi 3 workers initially slows computation before the parallelism benefit kicks in.

---

### MPI Monte Carlo Pi — Gustafson's Law (Weak Scaling)

**Configuration:** Problem size scales with processes (100M points × np)

| Processes | Points | Time (s) | Gustafson Speedup |
|-----------|--------|---------|-------------------|
| 1 | 100M | 1.605 | 1.00x |
| 2 | 200M | 8.276 | 0.39x |
| 4 | 400M | 8.277 | 0.78x |
| 8 | 800M | 12.700 | 1.01x |
| 16 | 1,600M | 14.451 | 1.78x |
| 28 | 2,800M | 16.957 | 2.65x |

**Key Observations:**
- With 28 processes we compute **28× more work** in only **10× the time**
- Speedup improves as problem size grows — Gustafson's Law confirmed
- At np=8, we compute 8× more work in only 8× the time — near-linear scaling!

**Conclusion:**
Gustafson's Law demonstrates that weak scaling (growing problem with processors) performs much better than strong scaling (Amdahl's). When the workload grows proportionally with the number of processors, the serial overhead becomes a smaller fraction of total work. This is the practical reality of cluster computing — add more nodes AND solve bigger problems.

---

### HPL/LINPACK Benchmark — Strong Scaling

**Configuration:** N=7000, NB=64, P=1, Q=np

| Processes | GFlops | Time (s) | Status |
|-----------|--------|---------|--------|
| 1 | 12.988 | 17.61 | ✅ PASSED |
| 2 | 2.192 | 104.37 | ✅ PASSED |
| 4 | 1.543 | 148.27 | ✅ PASSED |
| 8 | 1.092 | 209.40 | ✅ PASSED |
| 16 | 0.586 | 390.48 | ✅ PASSED |
| 28 | 0.355 | 643.96 | ❌ FAILED |

**Key Observations:**
- Pi 5 alone (np=1) achieves **12.988 GFlops** — by far the best performance
- Adding Pi 3 workers consistently DECREASES performance
- Performance drops monotonically with more nodes
- np=28 fails the residual check — numerical instability with Q=28 process grid

**Conclusion:**
HPL results show the dramatic effect of hardware heterogeneity. The Pi 5 (Cortex-A76 @ 2.4GHz, 8GB LPDDR4X) is approximately **3-4× faster** than Pi 3 workers (Cortex-A53 @ 1.2GHz, 1GB LPDDR2). In distributed HPL, the slowest node determines the pace of all others — a classic bottleneck effect. The communication overhead of MPI collective operations (broadcast, all-reduce) over Gigabit Ethernet adds latency at every step. For heterogeneous clusters like ours, HPL is best run on the fastest node alone.

**Why does performance drop so dramatically?**
HPL requires O(n²) communication per O(n³/p) computation. As p increases, the computation per node decreases but communication stays constant, making communication the dominant factor. This is a fundamental limitation of dense linear algebra on distributed memory systems.

---

## Task 4 — Task Distributor (Non-MPI)

### Task Distributor — Amdahl's Law (Fixed Image 800×600)

| Nodes | Time (s) | Speedup | Parallel Part (s) |
|-------|---------|---------|-------------------|
| 1 | 5.166 | 1.00x | 5.020 |
| 2 | 7.534 | 0.69x | 7.030 |
| 4 | 6.675 | 0.77x | 6.033 |
| 7 | 9.995 | 0.52x | 9.060 |

**Key Observations:**
- More nodes = SLOWER for fixed small image
- SSH connection overhead + NFS file transfer dominates
- Sequential parts (lockfile creation, image assembly) are constant

**Conclusion:**
For a fixed 800×600 image, the communication overhead (SSH setup + NFS file transfer of image parts) completely dominates the computation time. The serial fraction exceeds 50%, meaning Amdahl's Law predicts no speedup is possible. This demonstrates that Task Distributor is only efficient when the computation (POV-Ray rendering) is significantly larger than the communication (file transfer). Small images are entirely in the communication-dominated regime.

---

### Task Distributor — Gustafson's Law (Scaled Image)

| Nodes | Image Size | Pixels | Time (s) | Pixel Throughput |
|-------|-----------|--------|---------|-----------------|
| 1 | 320×240 | 76,800 | 4.162 | 18,453 px/s |
| 2 | 640×480 | 307,200 | 4.370 | 70,298 px/s |
| 4 | 1280×960 | 1,228,800 | 6.825 | 180,044 px/s |
| 7 | 2240×1680 | 3,763,200 | 19.730 | 190,735 px/s |

**Key Observations:**
- n=1 vs n=2: nearly same time (4.16s vs 4.37s) but **4× more pixels rendered!**
- n=2 vs n=4: 4× more pixels, 1.56× more time → good scaling
- n=7 becomes NFS-bottlenecked (large image transfer over network)
- Pixel throughput increases from 18K to 190K px/s — **10× improvement!**

**Conclusion:**
Gustafson's Law is clearly demonstrated when the problem scales with workers. At n=2, we processed 4× more image content in essentially the same time as n=1 processing 1× content. This confirms that weak scaling (matching workload to resources) is the correct approach for distributed computing. The degradation at n=7 illustrates a real-world limitation: NFS network bandwidth becomes the bottleneck when transferring large (2240×1680) image parts.

---

## Overall Takeaway

### What We Learned

**1. Hardware heterogeneity matters:**
Pi 5 is 3-4× faster than Pi 3. In any distributed computation, the slowest node limits the entire cluster. For HPL, it was always better to use Pi 5 alone.

**2. Communication overhead is real:**
SSH connection setup (~0.5s), MPI_Reduce, and NFS file transfer all add serial overhead that limits parallel efficiency. This is exactly what Amdahl predicted in 1967.

**3. Amdahl's Law is a ceiling, not a target:**
With serial fraction s=0.44, maximum speedup = 2.27×. No amount of hardware can overcome this without reducing the serial fraction.

**4. Gustafson's Law offers a path forward:**
When we scale the problem with the hardware, scaling efficiency improves dramatically. This is why modern HPC systems work on larger problems as they grow, not just the same problem faster.

**5. The right tool for the right job:**
- Embarrassingly parallel + large work → scales well (Gustafson)
- Communication-heavy + small work → Amdahl's wall
- Mixed hardware → use the fastest node for sequential-heavy work

### General Formula

```
Amdahl:    Speedup_strong(p) = 1 / (s + (1-s)/p)
Gustafson: Speedup_weak(p)   = p - s(p-1)
Efficiency: E(p) = Speedup(p) / p × 100%
Serial fraction: s = (1/Speedup - 1/p) / (1 - 1/p)
```

### Our Measured Serial Fractions

| Benchmark | Serial Fraction | Cause |
|-----------|----------------|-------|
| MPI Monte Carlo (100M) | ~44% | SSH + MPI_Reduce |
| MPI Monte Carlo (1B+) | ~5% | Computation dominates |
| Task Distributor (800×600) | >50% | SSH + NFS transfer |
| Task Distributor (scaled) | ~10% | NFS bottleneck only |

---

*Frankfurt University of Applied Sciences — Cloud Computing SS2026 — Group 8*
*Prof. Dr. Christian Baun*
