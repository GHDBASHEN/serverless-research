# benchmarks/micro/io_intensive/disk_io.py
import time
import json
import os
import random

def handler(event, context):
    """Test ephemeral disk I/O performance"""
    start_time = time.time()
    
    file_size_mb = event.get('file_size_mb', 10)
    file_path = '/tmp/benchmark_test.tmp'
    chunk_size = 1024 * 1024 # 1 MB chunks
    
    # Write Phase
    write_start = time.time()
    with open(file_path, 'wb') as f:
        for _ in range(file_size_mb):
            # Write 1MB of random bytes
            f.write(os.urandom(chunk_size))
    write_time = (time.time() - write_start) * 1000
    
    # Read Phase
    read_start = time.time()
    bytes_read = 0
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            bytes_read += len(chunk)
    read_time = (time.time() - read_start) * 1000
    
    # Cleanup
    os.remove(file_path)
    
    execution_time = (time.time() - start_time) * 1000
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'file_size_mb': file_size_mb,
            'bytes_read': bytes_read,
            'write_time_ms': write_time,
            'read_time_ms': read_time,
            'execution_time_ms': execution_time,
            'function': 'disk_io',
            'workload_type': 'io_intensive'
        })
    }

if __name__ == '__main__':
    print(handler({'file_size_mb': 5}, None))
