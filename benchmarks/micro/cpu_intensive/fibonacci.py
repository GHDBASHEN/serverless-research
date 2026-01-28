# benchmarks/micro/cpu_intensive/fibonacci.py
import time
import json

def fibonacci_recursive(n):
    """Calculate fibonacci recursively (CPU-intensive)"""
    if n <= 1:
        return n
    return fibonacci_recursive(n-1) + fibonacci_recursive(n-2)

def handler(event, context):
    """
    AWS Lambda handler
    For Azure/GCP, we'll create adapters
    """
    start_time = time.time()
    
    # Parse input
    n = event.get('n', 30)  # Default to fib(30)
    
    # Execute
    result = fibonacci_recursive(n)
    
    # Calculate metrics
    execution_time = (time.time() - start_time) * 1000  # Convert to ms
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'result': result,
            'n': n,
            'execution_time_ms': execution_time,
            'function': 'fibonacci_recursive',
            'workload_type': 'cpu_intensive'
        })
    }

# For local testing
if __name__ == '__main__':
    test_event = {'n': 30}
    print(handler(test_event, None))