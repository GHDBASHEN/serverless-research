"""
================================================================================
MICRO-BENCHMARK: Memory-Intensive Computing Primitives
================================================================================
Focuses on evaluating dynamic RAM allocation speed, heap management,
hash-map / dictionary collisions, and large contiguous buffer operations.
================================================================================
"""

import sys
import time


def memory_heap_allocation(num_elements: int = 500000) -> int:
    """
    Allocates a large list of string/object elements in the Python heap.
    Tests dynamic memory provisioning and garbage collector footprint.
    """
    buffer = [f"payload_record_index_{i}_val_{i * 3}" for i in range(num_elements)]
    size_bytes = sys.getsizeof(buffer)
    # Touch elements to force resident physical memory paging
    checksum = sum(len(x) for x in buffer[:1000])
    del buffer
    return checksum


def memory_dict_lookups(num_items: int = 200000) -> float:
    """
    Large hash table (dict) creation, hashing, lookup, and mutation.
    Tests dictionary rehashing overhead and hash-table random access.
    """
    hash_table = {f"item_uuid_{i}": i * 2.5 for i in range(num_items)}
    
    # Perform random-order lookups
    total = 0.0
    for i in range(0, num_items, 2):
        key = f"item_uuid_{i}"
        total += hash_table.get(key, 0.0)

    del hash_table
    return total


def memory_large_string_concatenation(chunks: int = 50000) -> int:
    """
    Continuous string buffer growth and concatenation.
    Tests string interning, memory reallocations, and copying overhead.
    """
    chunk = "A" * 64
    accumulator = []
    for _ in range(chunks):
        accumulator.append(chunk)

    final_str = "".join(accumulator)
    length = len(final_str)
    del final_str, accumulator
    return length


if __name__ == "__main__":
    print("Running Memory Micro-Benchmarks...")
    t0 = time.perf_counter()
    memory_heap_allocation(200000)
    print(f"  Heap Allocation (200k items)  : {(time.perf_counter()-t0)*1000:.2f} ms")
    t0 = time.perf_counter()
    memory_dict_lookups(100000)
    print(f"  Dict Lookups (100k items)     : {(time.perf_counter()-t0)*1000:.2f} ms")
    t0 = time.perf_counter()
    memory_large_string_concatenation(30000)
    print(f"  String Concatenation (30k)    : {(time.perf_counter()-t0)*1000:.2f} ms")
