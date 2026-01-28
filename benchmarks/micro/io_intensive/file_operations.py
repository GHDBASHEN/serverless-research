# benchmarks/micro/io_intensive/file_operations.py
import time
import json
import boto3
import os

def handler(event, context):
    """Read and write to object storage"""
    start_time = time.time()
    
    # Get parameters
    file_size_kb = event.get('file_size_kb', 1024)  # 1MB default
    
    # Create dummy data
    data = 'x' * (file_size_kb * 1024)
    
    # Write to /tmp (local storage)
    tmp_file = '/tmp/test_file.txt'
    write_start = time.time()
    with open(tmp_file, 'w') as f:
        f.write(data)
    write_time = (time.time() - write_start) * 1000
    
    # Read from /tmp
    read_start = time.time()
    with open(tmp_file, 'r') as f:
        read_data = f.read()
    read_time = (time.time() - read_start) * 1000
    
    # Upload to S3 (if AWS) or equivalent
    s3_start = time.time()
    try:
        s3 = boto3.client('s3')
        bucket = os.environ.get('BUCKET_NAME', 'your-test-bucket')
        s3.put_object(Bucket=bucket, Key='test_file.txt', Body=data)
        s3_upload_time = (time.time() - s3_start) * 1000
    except:
        s3_upload_time = None
    
    execution_time = (time.time() - start_time) * 1000
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'file_size_kb': file_size_kb,
            'write_time_ms': write_time,
            'read_time_ms': read_time,
            's3_upload_time_ms': s3_upload_time,
            'total_time_ms': execution_time,
            'function': 'file_operations',
            'workload_type': 'io_intensive'
        })
    }