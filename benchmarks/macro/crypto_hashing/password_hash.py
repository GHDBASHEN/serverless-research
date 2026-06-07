# benchmarks/macro/crypto_hashing/password_hash.py
import time
import json
import hashlib
import os

def handler(event, context):
    """Simulate authentication/security password hashing"""
    start_time = time.time()
    
    iterations = event.get('iterations', 100000)
    passwords_to_hash = event.get('count', 5)
    
    hash_start = time.time()
    results = []
    for i in range(passwords_to_hash):
        password = f"dummy_password_to_hash_{i}".encode('utf-8')
        salt = os.urandom(16)
        
        # pbkdf2 is a standard CPU-intensive hashing algorithm
        hashed = hashlib.pbkdf2_hmac(
            'sha256', 
            password, 
            salt, 
            iterations
        )
        results.append(hashed.hex())
        
    hash_time = (time.time() - hash_start) * 1000
    execution_time = (time.time() - start_time) * 1000
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'iterations': iterations,
            'count': passwords_to_hash,
            'hash_time_ms': hash_time,
            'execution_time_ms': execution_time,
            'function': 'password_hash',
            'workload_type': 'crypto'
        })
    }

if __name__ == '__main__':
    print(handler({'iterations': 10000, 'count': 2}, None))
