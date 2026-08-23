# HPL Results

![HPL Benchmark](../assets/graphs/hpl_benchmark.png)

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

