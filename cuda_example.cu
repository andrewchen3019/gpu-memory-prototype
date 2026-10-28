// Optional next step: real CUDA version of the interleaved benchmark.
// NOT validated with nvcc or a GPU. No cuBLAS or kernels are used.
// Prints expected answers, not measurements from the team's profiler.
// The profiler must observe only the marked window for an exact comparison.
#include <cuda_runtime_api.h>
#include <cstdio>
#include <cstdlib>

void check(cudaError_t result) {
    if (result != cudaSuccess) {
        std::fprintf(stderr, "CUDA call failed, status=%d\n", (int)result);
        std::exit(1);
    }
}

int main() {
    const size_t MiB = 1024 * 1024;
    void *a = nullptr, *b = nullptr, *c = nullptr;

    // Initialization occurs BEFORE the test window.
    check(cudaSetDevice(0));
    void* warmup = nullptr;
    check(cudaMalloc(&warmup, 1));
    check(cudaFree(warmup));

    // These print statements are human markers, NOT profiler-control hooks.
    std::puts("BEGIN TEST WINDOW");
    std::fflush(stdout);

    check(cudaMalloc(&a, 64 * MiB));
    std::puts("Allocated A: expected current=64 MiB, peak=64 MiB");

    check(cudaMalloc(&b, 128 * MiB));
    std::puts("Allocated B: expected current=192 MiB, peak=192 MiB");

    check(cudaFree(a));
    std::puts("Freed A: expected current=128 MiB, peak=192 MiB");

    check(cudaMalloc(&c, 96 * MiB));
    std::puts("Allocated C: expected current=224 MiB, peak=224 MiB");

    check(cudaFree(b));
    check(cudaFree(c));
    std::puts("Freed B and C: expected current=0 MiB, peak=224 MiB");

    std::puts("END TEST WINDOW");
    std::puts("Compare profiler output to expected peak=234881024 bytes.");
    return 0;
}
