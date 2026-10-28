"""Small CPU-only prototype: three known-answer memory benchmarks.

No GPU, CUDA, or extra Python packages needed. All sizes are integer bytes.
The tracker below is a stand-in for Ethan's code, not his implementation.
Scope: successful synchronous allocations/frees on one device, with unique
live pointer IDs. No async operations, failures, caching, or rollback yet.
"""

MIB = 1024 * 1024


class DemoTracker:
    def __init__(self):
        self.allocations = {}   # pointer ID -> number of bytes still allocated
        self.current_bytes = 0
        self.peak_bytes = 0

    def allocate(self, pointer, size_bytes):
        if pointer in self.allocations:
            raise ValueError("Pointer is already allocated")
        self.allocations[pointer] = size_bytes
        self.current_bytes += size_bytes
        self.peak_bytes = max(self.peak_bytes, self.current_bytes)

    def free(self, pointer):
        size_bytes = self.allocations.pop(pointer)
        self.current_bytes -= size_bytes


def run_benchmark(name, steps, expected_current_mib, expected_peak_mib):
    tracker = DemoTracker()  # Each benchmark starts with empty state.
    if len(steps) != len(expected_current_mib):
        raise ValueError("Each step needs an expected current-memory value")

    print("\n" + name)
    print("Operation          Current (MiB)   Peak (MiB)")
    for i, (operation, pointer, size_mib) in enumerate(steps):
        if operation == "alloc":
            tracker.allocate(pointer, size_mib * MIB)
        elif operation == "free":
            tracker.free(pointer)
        else:
            raise ValueError("Unknown operation")

        print(f"{operation + ' ' + pointer:<18} "
              f"{tracker.current_bytes // MIB:>13} {tracker.peak_bytes // MIB:>12}")
        # These answers were calculated by hand, not by DemoTracker.
        if tracker.current_bytes != expected_current_mib[i] * MIB:
            raise AssertionError(f"Wrong current memory after step {i + 1}")
        if tracker.peak_bytes != max(expected_current_mib[:i + 1]) * MIB:
            raise AssertionError(f"Wrong peak memory after step {i + 1}")

    if tracker.peak_bytes != expected_peak_mib * MIB:
        raise AssertionError("Wrong final peak")
    print(f"PASS: expected peak = {expected_peak_mib} MiB")


def main():
    print("CPU-ONLY DEMO: synthetic events + a stand-in tracker.")
    print("This does not test CUDA, the emulator, or Ethan's implementation yet.")

    run_benchmark("1. One allocation", [
        ("alloc", "A", 64),
        ("free", "A", 0),
    ], expected_current_mib=[64, 0], expected_peak_mib=64)

    run_benchmark("2. Sequential allocations", [
        ("alloc", "A", 64),
        ("free", "A", 0),
        ("alloc", "B", 128),
        ("free", "B", 0),
    ], expected_current_mib=[64, 0, 128, 0], expected_peak_mib=128)

    run_benchmark("3. Interleaved allocations", [
        ("alloc", "A", 64),
        ("alloc", "B", 128),
        ("free", "A", 0),
        ("alloc", "C", 96),
        ("free", "B", 0),
        ("free", "C", 0),
    ], expected_current_mib=[64, 192, 128, 224, 96, 0], expected_peak_mib=224)

    print("\nAll 3 benchmarks passed against DemoTracker.")


if __name__ == "__main__":
    main()
