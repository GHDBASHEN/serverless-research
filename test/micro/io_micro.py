"""
================================================================================
MICRO-BENCHMARK: Disk I/O & Filesystem Primitives
================================================================================
Measures serverless ephemeral storage (/tmp) write and read throughput,
file chunk streaming, and filesystem operations.
================================================================================
"""

import os
import random
import time
from pathlib import Path


def io_file_write_and_read(size_kb: int = 5120) -> int:
    """
    Writes sequential binary blocks to a temporary file and reads them back.
    Tests filesystem write buffer throughput and read caching.
    """
    temp_file = Path(f"./temp_bench_io_{random.randint(10000, 99999)}.tmp")
    chunk_1kb = b"D" * 1024
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


def io_csv_line_parsing(num_lines: int = 20000) -> int:
    """
    Generates and parses an in-memory CSV text stream line by line.
    Tests string splitting, field extraction, and stream iteration.
    """
    sample_lines = [
        f"2026-09-17T12:00:{i%60:02d},serverless_func_{i%10},aws,200,{i*1.23:.2f}"
        for i in range(num_lines)
    ]
    raw_csv = "\n".join(sample_lines)

    parsed_count = 0
    for line in raw_csv.splitlines():
        parts = line.split(",")
        if len(parts) == 5:
            parsed_count += 1

    return parsed_count


if __name__ == "__main__":
    print("Running Disk/IO Micro-Benchmarks...")
    t0 = time.perf_counter()
    bytes_done = io_file_write_and_read(2048)  # 2MB
    print(f"  File Write/Read (2MB) : {bytes_done / 1e6:.2f} MB in {(time.perf_counter()-t0)*1000:.2f} ms")
    t0 = time.perf_counter()
    lines_done = io_csv_line_parsing(20000)
    print(f"  CSV Line Parsing (20k): {lines_done} lines in {(time.perf_counter()-t0)*1000:.2f} ms")
