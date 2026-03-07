# Testing only 


#!/usr/bin/env python3
"""
Benchmark script for PII processing performance.
Run with: python benchmark.py
"""

import time
import statistics
from backend.utils import process_text

# Test cases of varying lengths
TEST_CASES = [
    ("Short", "Rahul Sharma"),
    ("Medium", "Rahul Sharma email rahul@gmail.com phone 9876543210"),
    ("Long", "John Doe (john@doe.com) called 555-1234. " * 10),
    ("Mixed", "Alice and Bob met at 123 Main St. Contact alice@work.com or 555-5678.")
]

def benchmark(func, text, iterations=10):
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        func(text)
        end = time.perf_counter()
        times.append((end - start) * 1000)  # ms
    return times

def main():
    print("=== Performance Benchmark ===\n")
    for name, text in TEST_CASES:
        print(f"Test: {name} (length {len(text)} chars)")
        times = benchmark(lambda t: process_text(t), text, iterations=10)
        avg = statistics.mean(times)
        max_t = max(times)
        min_t = min(times)
        print(f"  Min: {min_t:.2f}ms, Max: {max_t:.2f}ms, Avg: {avg:.2f}ms")
        print()

if __name__ == "__main__":
    main()