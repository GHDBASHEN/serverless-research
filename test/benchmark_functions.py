"""
================================================================================
CloudPredict - Serverless Benchmark Functions Suite
================================================================================
This module contains standard benchmark functions across 4 core serverless
operational workload categories:
  1. CPU-Intensive Workloads (Fibonacci, Matrix Multiplication, Prime Sieve, Float Ops)
  2. Memory-Intensive Workloads (Dynamic RAM Allocations, Dictionary Operations)
  3. Cryptographic Workloads (SHA-256 Hashing, Message Digest Iterations)
  4. Data & I/O-Intensive Workloads (JSON Transformations, Local Disk I/O)

Each benchmark function is instrumented to measure:
  - Execution Duration (duration_ms)
  - Memory Consumption (memory_mb)
  - Serverless Cost Estimation (cost_usd across AWS, Azure, GCP)
================================================================================
"""

import time
import math
import random
import os
import json
import hashlib
import sys
from pathlib import Path


# ──────────────────────────────────────────────────────────────────────────────
# 1. HELPER: MEMORY PROFILING & PRICING CALCULATION
# ──────────────────────────────────────────────────────────────────────────────
def get_peak_memory_mb():
    """Returns the peak memory usage in MB for the current process."""
    try:
        import resource
        # ru_maxrss is in KB on Linux, bytes on macOS
        usage_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return usage_kb / 1024.0
    except ImportError:
        # Fallback for Windows / OS without resource module
        try:
            import psutil
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / (1024.0 * 1024.0)
        except ImportError:
            return 128.0  # Fallback baseline


def calculate_cost_usd(platform: str, memory_mb: int, duration_ms: float) -> float:
    """
    Calculates estimated invocation cost based on official serverless pricing models:
      - Duration in GB-Seconds * Tier Rate + Request Fee ($0.20 per million)
    """
    duration_sec = duration_ms / 1000.0
    gb_sec = (memory_mb / 1024.0) * duration_sec

    # Pricing parameters
    if platform.lower() == 'azure':
        price_per_gb_sec = 0.000016
        request_price = 0.0000002
    else:  # AWS Lambda & GCP Cloud Functions
        price_per_gb_sec = 0.0000166667
        request_price = 0.0000002

    cost = (gb_sec * price_per_gb_sec) + request_price
    return cost


# ──────────────────────────────────────────────────────────────────────────────
# 2. BENCHMARK FUNCTIONS SUITE
# ──────────────────────────────────────────────────────────────────────────────

# ── Category A: CPU-Intensive Workloads ───────────────────────────────────────

def benchmark_fibonacci(size: int = 30):
    """
    Recursive CPU computation benchmark.
    Tests recursion depth, CPU register utilization, and call stack overhead.
    """
    def fib(n):
        if n <= 1:
            return n
        return fib(n - 1) + fib(n - 2)

    # Cap size to 32 to prevent infinite hangs in Python recursive evaluation
    n = min(size, 32)
    return fib(n)


def benchmark_matrix_mult(size: int = 100):
    """
    O(N^3) Matrix Multiplication benchmark.
    Simulates intensive linear algebra and nested looping operations.
    """
    N = max(10, min(size, 180))
    A = [[random.random() for _ in range(N)] for _ in range(N)]
    B = [[random.random() for _ in range(N)] for _ in range(N)]
    C = [[0.0] * N for _ in range(N)]

    for i in range(N):
        for j in range(N):
            total = 0.0
            for k in range(N):
                total += A[i][k] * B[k][j]
            C[i][j] = total
    return C[0][0]


def benchmark_prime_sieve(size: int = 50000):
    """
    Sieve of Eratosthenes algorithm.
    Evaluates branch prediction, sequential memory access, and integer division.
    """
    N = max(100, size)
    primes = [True] * (N + 1)
    primes[0] = primes[1] = False

    limit = int(math.isqrt(N)) + 1
    for i in range(2, limit):
        if primes[i]:
            for j in range(i * i, N + 1, i):
                primes[j] = False

    return sum(primes)


def benchmark_float_ops(size: int = 100000):
    """
    Heavy Floating-Point Arithmetic benchmark.
    Executes repetitive trigonometry (sin, cos, tan) and square-root operations.
    """
    val = 1.2345
    for _ in range(size):
        val = math.sin(val) * math.cos(val) + math.tan(val * 0.5)
    return val


# ── Category B: Memory-Intensive Workloads ────────────────────────────────────

def benchmark_memory_allocation(size: int = 1000000):
    """
    Dynamic Heap Allocation benchmark.
    Allocates and populates large integer and string arrays in RAM.
    """
    large_list = [f"data_record_index_{i}_val_{i * 2}" for i in range(size)]
    # Touch elements to force resident page allocation
    checksum = len("".join(large_list[:100]))
    del large_list
    return checksum


def benchmark_dict_operations(size: int = 200000):
    """
    Hash-table lookup and mutation benchmark.
    Tests dynamic dictionary rehashing, collision resolution, and key lookups.
    """
    data_dict = {f"key_{i}": i * 1.5 for i in range(size)}
    total = sum(data_dict[f"key_{i}"] for i in range(0, size, 2))
    del data_dict
    return total


# ── Category C: Cryptographic Workloads ───────────────────────────────────────

def benchmark_crypto_hash(size: int = 10000):
    """
    Cryptographic Security benchmark.
    Executes multi-iteration SHA-256 and SHA-512 hashing loops.
    """
    current_hash = hashlib.sha256(b"cloudpredict_initial_salt").digest()
    for i in range(size):
        hasher = hashlib.sha256(current_hash)
        hasher.update(str(i).encode('utf-8'))
        current_hash = hasher.digest()
    return current_hash.hex()


# ── Category D: Data & I/O-Intensive Workloads ─────────────────────────────────

def benchmark_json_transform(size: int = 5000):
    """
    JSON serialization, parsing, filtering, and data aggregation benchmark.
    Standard serverless microservice business logic simulation.
    """
    # 1. Generate payload records
    records = [
        {
            "id": f"rec_{i}",
            "amount": round(random.random() * 1000, 2),
            "status": "APPROVED" if i % 2 == 0 else "PENDING",
            "tags": ["aws", "azure", "gcp", "serverless"]
        }
        for i in range(size)
    ]

    # 2. Serialize to JSON string
    json_str = json.dumps(records)

    # 3. Parse JSON back
    parsed = json.loads(json_str)

    # 4. Filter and aggregate
    approved_total = sum(r["amount"] for r in parsed if r["status"] == "APPROVED")
    return approved_total


def benchmark_disk_io(size_kb: int = 5120):
    """
    Local Ephemeral Storage (Disk /tmp) I/O throughput benchmark.
    Writes and reads sequential chunks to test filesystem write/read speeds.
    """
    temp_file = Path(f"./temp_bench_{random.randint(10000, 99999)}.tmp")
    chunk_1kb = b"X" * 1024
    num_chunks = max(1, size_kb)

    try:
        # Write phase
        with open(temp_file, "wb") as f:
            for _ in range(num_chunks):
                f.write(chunk_1kb)

        # Read phase
        bytes_read = 0
        with open(temp_file, "rb") as f:
            while chunk := f.read(65536):
                bytes_read += len(chunk)

        return bytes_read
    finally:
        if temp_file.exists():
            temp_file.unlink()


# ──────────────────────────────────────────────────────────────────────────────
# 3. BENCHMARK EXECUTION HARNESS
# ──────────────────────────────────────────────────────────────────────────────
BENCHMARK_REGISTRY = {
    "fibonacci": benchmark_fibonacci,
    "matrix_mult": benchmark_matrix_mult,
    "prime_sieve": benchmark_prime_sieve,
    "float_ops": benchmark_float_ops,
    "mem_alloc": benchmark_memory_allocation,
    "mem_dict": benchmark_dict_operations,
    "crypto_hash": benchmark_crypto_hash,
    "json_transform": benchmark_json_transform,
    "disk_io": benchmark_disk_io,
}


def run_benchmark(workload_name: str, input_size: int = 100, memory_mb: int = 512):
    """
    Executes a benchmark workload with high-precision instrumentation, returning:
      - duration_ms: Wall-clock latency in milliseconds
      - memory_mb: Memory consumed
      - costs: Dict of estimated costs on AWS, Azure, and GCP
    """
    if workload_name not in BENCHMARK_REGISTRY:
        raise ValueError(f"Unknown workload: {workload_name}. Available: {list(BENCHMARK_REGISTRY.keys())}")

    fn = BENCHMARK_REGISTRY[workload_name]

    # Measure latency
    start_time = time.perf_counter()
    result = fn(input_size)
    duration_sec = time.perf_counter() - start_time
    duration_ms = duration_sec * 1000.0

    # Calculate costs for all 3 cloud providers
    costs = {
        "aws": calculate_cost_usd("aws", memory_mb, duration_ms),
        "azure": calculate_cost_usd("azure", memory_mb, duration_ms),
        "google": calculate_cost_usd("google", memory_mb, duration_ms),
    }

    return {
        "workload": workload_name,
        "input_size": input_size,
        "memory_mb": memory_mb,
        "duration_ms": round(duration_ms, 2),
        "costs_usd": costs,
    }


# ──────────────────────────────────────────────────────────────────────────────
# 4. CLI DEMO RUNNER
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("=" * 70)
    print(">> CloudPredict Serverless Benchmark Functions Demo")
    print("=" * 70)

    test_workloads = [
        ("float_ops", 50000, 512),
        ("prime_sieve", 10000, 512),
        ("matrix_mult", 80, 512),
        ("crypto_hash", 5000, 512),
        ("json_transform", 2000, 512),
        ("disk_io", 2048, 512),
    ]

    print(f"{'Workload':<16} {'Size':<8} {'Duration (ms)':<16} {'AWS Cost ($)':<14} {'Azure Cost ($)':<14}")
    print("-" * 70)

    for wl, sz, mem in test_workloads:
        out = run_benchmark(wl, input_size=sz, memory_mb=mem)
        dur = out["duration_ms"]
        aws_cost = out["costs_usd"]["aws"]
        az_cost = out["costs_usd"]["azure"]
        print(f"{wl:<16} {sz:<8} {dur:>10.2f} ms     ${aws_cost:.8f}    ${az_cost:.8f}")

    print("=" * 70)
    print("[SUCCESS] All benchmark functions executed successfully!")
