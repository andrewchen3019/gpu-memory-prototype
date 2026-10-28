# Simple GPU memory benchmark prototype

## Run on your Windows VCM

Extract this folder. Open PowerShell in it and run:

```powershell
py -3 benchmarks.py
```

If the `py` launcher is unavailable but Python is installed:

```powershell
python benchmarks.py
```

Requires Python 3.6 or newer. No packages, GPU, CUDA, admin privileges, or Linux required. If neither command exists, install Python 3 or use a machine where it is already installed. Run from the folder containing benchmarks.py.

On Linux/macOS: `python3 benchmarks.py`.

## What this demonstrates

`benchmarks.py` contains three things:

1. **DemoTracker:** a tiny stand-in for Ethan's state machine. A dictionary stores live allocation sizes; two numbers hold current and peak bytes.
2. **Three benchmarks:** fixed allocation/free sequences with hand-calculated expected answers.
3. **run_benchmark:** feeds operations into the stand-in, prints each state, and checks current and peak bytes against those answers.

The benchmark sequences and checking logic are Andrew's proposed part. Ethan's actual tracker should replace the stand-in through a small adapter once its interface is available.

Python strings A/B/C are synthetic pointer IDs. The demo does NOT allocate GPU buffers, emulate CUDA, or execute the team's tracker. It only stores small bookkeeping records; the numeric sizes do not allocate corresponding CPU memory either.

## Three tests to explain

| Test | Operations | Expected peak |
|---|---|---:|
| One allocation | Allocate A=64 MiB; free A | 64 MiB |
| Sequential | Allocate/free A=64 MiB; allocate/free B=128 MiB | 128 MiB |
| Interleaved | Allocate A=64 and B=128; free A; allocate C=96; free B/C | 224 MiB |

The second test catches confusing cumulative allocated volume (192 MiB) with peak outstanding bytes (128 MiB). The third checks that a free reduces current memory while preserving the historical peak.

Interleaved current memory: 64 -> 192 -> 128 -> 224 -> 96 -> 0 MiB.
Interleaved peak memory: 64 -> 192 -> 192 -> 224 -> 224 -> 224 MiB.

Internally the tracker uses bytes. 1 MiB = 1,048,576 bytes. The third test peaks at 234,881,024 bytes. The initial scope assumes successful synchronous allocations/frees, one device, and a clean measurement window.

## Optional CUDA example

`cuda_example.cu` repeats the third test using cudaMalloc/cudaFree. It checks return codes and prints the EXPECTED values. It does not itself measure the profiler's accuracy. It needs a functioning CUDA environment or a sufficiently complete emulator; a Windows VCM alone does not guarantee either.

This source has not been compiled with nvcc or executed on a GPU here.

On a Linux CUDA development machine, a typical build is:

```bash
nvcc --cudart shared cuda_example.cu -o cuda_example
./cuda_example
```

The team's LD_PRELOAD approach is a Linux integration path. Use the Windows VCM for the Python demonstration; agree with Josh/Harouna on a Linux environment for emulator integration.

The CUDA example performs initialization before its marked test window. The BEGIN/END print messages do not automatically reset or control the team's profiler. Agree on actual start/stop/reset hooks or trace filtering before comparing whole-process capture output to the exact 224 MiB answer. Initialization allocations and driver overhead are outside that answer.

## What the Discord log establishes

- Josh/Harouna: capture and emulate runtime/driver/NVML calls; consistent device state is still in progress. Josh reports a cuBLAS problem involving undocumented function tables returned by cuGetExportTable.
- Ethan: has started tracking allocations, frees, peak memory, and state history for rollback.
- Andrew + Ethan: jointly assigned both tracker and microbenchmarks. Andrew taking benchmarks is a proposed division to confirm with Ethan.
- Matt: confirmed allocated bytes at the runtime/driver interface as the first metric; starting with sync APIs is approved.
- Rollback purpose and callback format are not settled by the supplied messages. Single-device scope is a proposed simplification.

## Meeting checklist

Be able to explain:

- Current bytes = sum of live allocations; peak = maximum current bytes seen so far.
- A free needs the saved allocation size, which is why the tracker stores a map.
- A benchmark is a controlled program with a known expected result.
- At the runtime/driver level, allocations retained by a framework cache remain allocated until freed at that level. These first tests do not exercise a framework cache.
- The CPU demo works independently of Josh's matrix-multiplication issue.
- Current status: basic reference demo tested; actual tracker integration and CUDA execution pending.

Get answers to:

1. Can Ethan own the tracker and Andrew own benchmarks/validation?
2. Can Ethan share his code, and Josh/Harouna share a callback header or example event?
3. Do events include the returned pointer, requested size, success/failure, device/context and ordering?
4. Which API layer is counted, so runtime and driver observations do not double-count an allocation?
5. How does a test reset state and define its measurement window? How are results exposed?
6. What triggers rollback, and is rollback part of the first milestone?
7. What repo, build/run command, and environment should everyone use? Where can real GPU validation run?
8. Agree on the next milestone: run these three cases against Ethan's tracker, then through the emulator.

## Suggested short update

I have a basic prototype with three allocation/free scenarios and hand-calculated expected peaks. It runs without a GPU using a small stand-in tracker, so it demonstrates the test sequences and checks rather than our actual integration. I also have a short CUDA version of the interleaved case, which still needs to be compiled and run in the team's environment. I'd like to take benchmarks and validation while Ethan owns the tracker. Next I need his interface and the capture layer's event format.

This is an AI-assisted starter. Review the code and run it yourself before describing what you have verified.

CUDA API reference: https://docs.nvidia.com/cuda/cuda-runtime-api/cuda_runtime_api/group__CUDART__MEMORY.html
