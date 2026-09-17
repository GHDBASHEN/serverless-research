"""
================================================================================
MICRO-BENCHMARK: CPU-Intensive Computing Primitives
================================================================================
Focuses on measuring pure raw CPU clock speed, branch prediction, 
register constraints, and mathematical throughput.
================================================================================
"""

import math
import random
import time


def cpu_fibonacci_recursive(n: int = 30) -> int:
    """
    Evaluates recursive function call overhead, call stack memory,
    and single-thread CPU compute speed.
    """
    def _fib(x):
        if x <= 1:
            return x
        return _fib(x - 1) + _fib(x - 2)

    limit = min(n, 32)  # Cap at 32 to avoid timeouts
    return _fib(limit)


def cpu_matrix_multiplication(size: int = 80) -> float:
    """
    O(N^3) dense matrix multiplication benchmark.
    Tests nested loop branch execution and continuous floating point math.
    """
    N = max(10, min(size, 150))
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


def cpu_prime_sieve(limit: int = 50000) -> int:
    """
    Sieve of Eratosthenes prime numbers finder.
    Evaluates sequential memory indexing, bit/bool operations, and CPU cache performance.
    """
    N = max(100, limit)
    primes = [True] * (N + 1)
    primes[0] = primes[1] = False

    limit_sqrt = int(math.isqrt(N)) + 1
    for i in range(2, limit_sqrt):
        if primes[i]:
            for j in range(i * i, N + 1, i):
                primes[j] = False

    return sum(primes)


def cpu_floating_point_math(iterations: int = 100000) -> float:
    """
    Repetitive trigonometry and floating-point math loop (sin, cos, tan, sqrt).
    Evaluates CPU Floating-Point Unit (FPU) throughput.
    """
    val = 1.2345
    for i in range(iterations):
        val = math.sin(val) * math.cos(val) + math.tan(val * 0.5)
    return val


if __name__ == "__main__":
    print("Running CPU Micro-Benchmarks...")
    t0 = time.perf_counter()
    print("  Fibonacci(30) :", cpu_fibonacci_recursive(30), f"({(time.perf_counter()-t0)*1000:.2f} ms)")
    t0 = time.perf_counter()
    print("  Matrix Mult(60):", f"done ({(time.perf_counter()-t0)*1000:.2f} ms)")
    cpu_matrix_multiplication(60)
    t0 = time.perf_counter()
    print("  Prime Sieve(30k):", cpu_prime_sieve(30000), f"({(time.perf_counter()-t0)*1000:.2f} ms)")
