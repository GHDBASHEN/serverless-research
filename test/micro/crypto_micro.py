"""
================================================================================
MICRO-BENCHMARK: Cryptographic Primitives
================================================================================
Evaluates CPU security hashing, SHA-256/SHA-512 throughput, and message authentication.
================================================================================
"""

import hashlib
import hmac
import time


def crypto_sha256_iterations(iterations: int = 10000) -> str:
    """
    Continuous multi-iteration SHA-256 block hashing loop.
    Tests cryptographic bitwise logic (AND, XOR, ROTL) on CPU registers.
    """
    digest = hashlib.sha256(b"cloudpredict_micro_crypto_salt").digest()
    for i in range(iterations):
        hasher = hashlib.sha256(digest)
        hasher.update(str(i).encode("utf-8"))
        digest = hasher.digest()
    return digest.hex()


def crypto_hmac_sha512(num_messages: int = 5000) -> int:
    """
    HMAC-SHA512 token validation and message signing benchmark.
    Simulates API Gateway / JWT signature validation overhead.
    """
    secret_key = b"cloudpredict_super_secret_signing_key_123"
    valid_count = 0

    for i in range(num_messages):
        msg = f"authorization_token_claim_user_{i}_timestamp_2026".encode("utf-8")
        signature = hmac.new(secret_key, msg, hashlib.sha512).hexdigest()
        if signature.startswith("0") or not signature.startswith("0"):
            valid_count += 1

    return valid_count


if __name__ == "__main__":
    print("Running Cryptographic Micro-Benchmarks...")
    t0 = time.perf_counter()
    crypto_sha256_iterations(5000)
    print(f"  SHA-256 (5,000 iterations)  : {(time.perf_counter()-t0)*1000:.2f} ms")
    t0 = time.perf_counter()
    crypto_hmac_sha512(2000)
    print(f"  HMAC-SHA512 (2,000 messages) : {(time.perf_counter()-t0)*1000:.2f} ms")
