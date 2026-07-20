/*
 * pi_mpi.c - Monte Carlo Pi Approximation using MPI
 * Cloud Computing SS2026 | Frankfurt UAS | Group 8
 *
 * Compile: mpicc pi_mpi.c -o pi_mpi
 * Run: mpirun --hostfile ~/cluster/benchmarks/mpi/hostfile -np 8 ./pi_mpi
 *
 * Demonstrates Amdahl's Law:
 * - Small problem (100M points): communication overhead dominates
 * - Large problem (1B points): computation dominates, better scaling
 */
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "mpi.h"

int main(int argc, char *argv[]) {
    int myid, nprocs;
    long int npts = 1e8;  // 100 million points (change to 1e9 for Gustafson's Law)
    long int i, mynpts;
    double f, sum, mysum;
    double xmin, xmax, x;

    MPI_Init(&argc, &argv);
    MPI_Comm_size(MPI_COMM_WORLD, &nprocs);
    MPI_Comm_rank(MPI_COMM_WORLD, &myid);

    /* Distribute work: rank 0 handles remainder */
    if (myid == 0) {
        mynpts = npts - (nprocs - 1) * (npts / nprocs);
    } else {
        mynpts = npts / nprocs;
    }

    mysum = 0.0;
    xmin = 0.0;
    xmax = 1.0;
    srand(time(0) + myid);  /* Different seed per rank */

    /* Monte Carlo integration: pi/4 = integral(0,1) 1/(1+x^2) dx */
    for (i = 0; i < mynpts; i++) {
        x = (double)rand() / RAND_MAX * (xmax - xmin) + xmin;
        mysum += 4.0 / (1.0 + x * x);
    }

    /* Collect results from all ranks */
    MPI_Reduce(&mysum, &sum, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);

    if (myid == 0) {
        f = sum / npts;
        printf("PI calculated with %ld points using %d processes = %.6f\n", npts, nprocs, f);
    }

    MPI_Finalize();
    return 0;
}
