"""
================================================================================
MACRO-BENCHMARK: Scientific Simulation & Numerical Computing
================================================================================
Simulates serverless scientific and analytical workloads:
  - Monte Carlo random sampling simulation (estimating Pi)
  - Numerical Trapezoidal integration
  - Pairwise Euclidean distance vector calculations
================================================================================
"""

import math
import random
import time


def monte_carlo_pi_estimation(num_samples: int = 150000) -> float:
    """
    Monte Carlo algorithm to approximate Pi using stochastic dart throws in a unit circle.
    Tests random number generation quality, conditional evaluations, and floating-point math.
    """
    inside_circle = 0
    for _ in range(num_samples):
        x = random.random()
        y = random.random()
        # Check if point falls within unit circle quadrant: x^2 + y^2 <= 1.0
        if (x * x + y * y) <= 1.0:
            inside_circle += 1

    pi_estimate = (4.0 * inside_circle) / num_samples
    return pi_estimate


def numerical_trapezoidal_integration(num_steps: int = 100000) -> float:
    """
    Approximates the definite integral of f(x) = sin(x) * exp(-x/5) from 0 to 10
    using the composite Trapezoidal Rule.
    """
    a = 0.0
    b = 10.0
    h = (b - a) / num_steps

    def f(x):
        return math.sin(x) * math.exp(-x / 5.0)

    total = 0.5 * (f(a) + f(b))
    for i in range(1, num_steps):
        total += f(a + i * h)

    return total * h


def vector_pairwise_distances(num_vectors: int = 300, dims: int = 10) -> float:
    """
    Computes pairwise Euclidean distance matrix across high-dimensional vectors.
    Tests multi-dimensional array math and nested vector loops.
    """
    # Generate vectors
    vectors = [[random.random() for _ in range(dims)] for _ in range(num_vectors)]

    sum_distances = 0.0
    for i in range(num_vectors):
        for j in range(i + 1, num_vectors):
            dist_sq = sum((vectors[i][d] - vectors[j][d]) ** 2 for d in range(dims))
            sum_distances += math.sqrt(dist_sq)

    return sum_distances


if __name__ == "__main__":
    print("Running Macro-Benchmark: Scientific Computing...")
    t0 = time.perf_counter()
    pi_val = monte_carlo_pi_estimation(100000)
    print(f"  Monte Carlo Pi (100k samples): {pi_val:.5f} in {(time.perf_counter()-t0)*1000:.2f} ms")
    t0 = time.perf_counter()
    integral = numerical_trapezoidal_integration(80000)
    print(f"  Trapezoidal Integral (80k)   : {integral:.5f} in {(time.perf_counter()-t0)*1000:.2f} ms")
    t0 = time.perf_counter()
    vec_sum = vector_pairwise_distances(200, 8)
    print(f"  Pairwise Vector Dist (200x8) : {vec_sum:.2f} in {(time.perf_counter()-t0)*1000:.2f} ms")
