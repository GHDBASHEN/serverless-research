import time
import json
import os
import math
import random
import sys

# Global variable to track cold starts
is_cold = True

def get_memory_usage():
    try:
        import resource
        # ru_maxrss is in KB on Linux, Bytes on MacOS. 
        # Assuming Linux (Lambda/Cloud Functions/Azure Linux Plan)
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    except ImportError:
        return 0.0

def handle(event, context):
    global is_cold
    start_time = time.time()
    
    # Parse input
    payload = event
    if isinstance(event, dict):
        if 'body' in event:
            try:
                if isinstance(event['body'], str):
                    payload = json.loads(event['body'])
                else:
                    payload = event['body']
            except:
                pass
        elif 'workload' not in event and 'req' in event: # Azure generic trigger sometimes wraps
             # This is a bit speculative for Azure Python v2 model, but we'll stick to a generic payload structure expectation
             pass

    # Fallback/Normalization
    # If the payload came in as a string in the body
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except:
            payload = {}
            
    workload = payload.get('workload', 'float_ops')
    size = int(payload.get('size', 1000))
    
    result = None
    
    if workload == 'fibonacci':
        # Recursive fibonacci is standard for CPU stress but hitting recursion limits or timeout on large N is risk.
        # We'll use iterative for safety or limit N in benchmarks config.
        # User requirement implies cpu stress.
        def fib(n):
            if n <= 1: return n
            return fib(n-1) + fib(n-2)
        # Warning: N > 35 is very slow in Python
        result = fib(size)
        
    elif workload == 'matrix_mult':
        N = size
        A = [[random.random() for _ in range(N)] for _ in range(N)]
        B = [[random.random() for _ in range(N)] for _ in range(N)]
        C = [[0] * N for _ in range(N)]
        for i in range(N):
            for j in range(N):
                for k in range(N):
                    C[i][j] += A[i][k] * B[k][j]
        result = C[0][0] # Just to ensure calculation is used
        
    elif workload == 'prime_sieve':
        N = size
        if N < 2:
            result = 0
        else:
            primes = [True] * (N + 1)
            primes[0] = primes[1] = False
            for i in range(2, int(math.sqrt(N)) + 1):
                if primes[i]:
                    for j in range(i*i, N + 1, i):
                        primes[j] = False
            result = sum(primes)
            
    elif workload == 'file_io':
        # Write 'size' bytes and read them back
        filename = f'/tmp/test_{random.randint(0, 1000000)}.txt'
        try:
            data_chunk = 'x' * 1024
            chunks = size // 1024
            remainder = size % 1024
            
            with open(filename, 'w') as f:
                for _ in range(chunks):
                    f.write(data_chunk)
                if remainder:
                    f.write('x' * remainder)
            
            with open(filename, 'r') as f:
                content = f.read()
                result = len(content)
        finally:
            if os.path.exists(filename):
                os.remove(filename)
        
    elif workload == 'float_ops':
        val = 1.0
        # simple loop of math ops
        for i in range(size):
            val = math.sin(val) * math.cos(val) + math.tan(val)
        result = val
        
    elif workload == 'json_transform':
        # Macro benchmark: data processing
        import string
        def generate_payload(num_records):
            records = []
            for i in range(num_records):
                records.append({
                    "id": i,
                    "uuid": "".join(random.choices(string.ascii_letters + string.digits, k=16)),
                    "amount": random.uniform(10.0, 1000.0),
                    "status": random.choice(["PENDING", "COMPLETED", "FAILED"]),
                    "metadata": {"source": "web", "tags": ["sale", "refund", "subscription"]}
                })
            return json.dumps({"batch_id": "test_batch", "records": records})
        
        payload_str = generate_payload(size)
        data = json.loads(payload_str)
        processed = []
        for record in data["records"]:
            if record["status"] == "COMPLETED":
                processed.append({
                    "id": record["id"],
                    "value": round(record["amount"] * 1.05, 2), # Add 5% tax
                })
        result = json.dumps({"processed_count": len(processed), "data": processed})
        
    elif workload == 'crypto_hash':
        # Macro benchmark: compute-intensive security
        import hashlib
        iterations = size
        passwords_to_hash = 5
        hashed_results = []
        for i in range(passwords_to_hash):
            password = f"dummy_password_to_hash_{i}".encode('utf-8')
            salt = os.urandom(16)
            hashed = hashlib.pbkdf2_hmac('sha256', password, salt, iterations)
            hashed_results.append(hashed.hex())
        result = len(hashed_results)


    elif workload == 'cpu_math_1':
        val = 0
        for i in range(size * 1000): val += math.sin(i)

    elif workload == 'cpu_math_2':
        val = 1
        for i in range(size * 100): val = (val * 1.0001) ** 1.01

    elif workload == 'cpu_math_3':
        val = 0
        for i in range(size * 500): val += math.factorial(i % 50)

    elif workload == 'cpu_math_4':
        val = sum([math.sqrt(i) for i in range(size * 1000)])

    elif workload == 'cpu_math_5':
        v1 = [random.random() for _ in range(size * 100)]
        v2 = [random.random() for _ in range(size * 100)]
        val = sum(x*y for x,y in zip(v1, v2))

    elif workload == 'mem_alloc_1':
        arr = [i for i in range(size * 10000)]

    elif workload == 'mem_alloc_2':
        arr = {str(i): i for i in range(size * 5000)}

    elif workload == 'mem_alloc_3':
        arr = [[i] * 10 for i in range(size * 2000)]

    elif workload == 'mem_string_4':
        s = ''.join(['x' for _ in range(size * 10000)])

    elif workload == 'mem_dict_5':
        d = {}
        for i in range(size * 1000): d[f'key_{i}'] = {'nested': i}

    elif workload == 'disk_io_1':
        f='/tmp/d1.txt'
        with open(f, 'w') as fh: fh.write('A' * size * 1000)
        os.remove(f)

    elif workload == 'disk_io_2':
        f='/tmp/d2.txt'
        with open(f, 'w') as fh: fh.write('B' * size * 2000)
        os.remove(f)

    elif workload == 'disk_io_3':
        f='/tmp/d3.txt'
        with open(f, 'wb') as fh: fh.write(os.urandom(size * 500))
        os.remove(f)

    elif workload == 'disk_io_4':
        f='/tmp/d4.txt'
        with open(f, 'w') as fh: 
            for i in range(size * 100): fh.write(str(i))
        os.remove(f)

    elif workload == 'disk_io_5':
        f='/tmp/d5.txt'
        with open(f, 'w') as fh: fh.write('X' * size * 100)
        with open(f, 'r') as fh: fh.read()
        os.remove(f)

    elif workload == 'net_sim_1':
        time.sleep(min(size * 0.001, 2))

    elif workload == 'net_sim_2':
        time.sleep(min(size * 0.002, 2))

    elif workload == 'net_sim_3':
        time.sleep(min(size * 0.003, 2))

    elif workload == 'net_sim_4':
        time.sleep(min(size * 0.004, 2))

    elif workload == 'net_sim_5':
        time.sleep(min(size * 0.005, 2))

    elif workload == 'data_proc_1':
        d = ','.join(str(i) for i in range(size * 100))
        val = len(d.split(','))

    elif workload == 'data_proc_2':
        j = json.dumps([{'id': i} for i in range(size * 100)])
        val = len(json.loads(j))

    elif workload == 'data_proc_3':
        import base64
        b = base64.b64encode(os.urandom(size * 100))
        base64.b64decode(b)

    elif workload == 'data_proc_4':
        val = len([x for x in range(size * 1000) if x % 2 == 0 and x % 3 == 0])

    elif workload == 'data_proc_5':
        import re
        s = 'abc 123 ' * (size * 100)
        val = len(re.findall(r'\d+', s))

    elif workload == 'crypto_1':
        import hashlib
        for i in range(size * 100): hashlib.md5(str(i).encode()).hexdigest()

    elif workload == 'crypto_2':
        import hashlib
        for i in range(size * 100): hashlib.sha1(str(i).encode()).hexdigest()

    elif workload == 'crypto_3':
        import hashlib
        for i in range(size * 100): hashlib.sha256(str(i).encode()).hexdigest()

    elif workload == 'crypto_4':
        import hashlib
        for i in range(size * 100): hashlib.sha512(str(i).encode()).hexdigest()

    elif workload == 'crypto_5':
        import hashlib
        hashlib.pbkdf2_hmac('sha256', b'pass', b'salt', size * 100)

    elif workload == 'web_biz_1':
        cart = [{'price': random.random()*100, 'qty': random.randint(1,5)} for _ in range(size * 10)]
        val = sum(i['price'] * i['qty'] for i in cart)

    elif workload == 'web_biz_2':
        users = [{'active': random.choice([True, False])} for _ in range(size * 100)]
        val = len([u for u in users if u['active']])

    elif workload == 'web_biz_3':
        html = '<h1>Header</h1>' * (size * 10)
        val = html.replace('h1>', 'h2>')

    elif workload == 'web_biz_4':
        val = ''.join(random.choices('abcdef', k=size * 100))

    elif workload == 'web_biz_5':
        items = [random.randint(0, 100) for _ in range(size * 100)]
        items.sort()

    elif workload == 'sci_1':
        data = [random.random() for _ in range(size * 100)]
        mean = sum(data)/len(data)
        val = sum((x-mean)**2 for x in data)

    elif workload == 'sci_2':
        x = [i for i in range(size * 100)]
        y = [i*2 + random.random() for i in range(size * 100)]
        val = sum(x) + sum(y)

    elif workload == 'sci_3':
        data = [random.random() for _ in range(size * 100)]
        val = [d / max(data) for d in data]

    elif workload == 'sci_4':
        val = sum(1 for _ in range(size * 100) if random.random()**2 + random.random()**2 <= 1) * 4 / (size * 100)

    elif workload == 'sci_5':
        val = sum(math.log(i) for i in range(1, size * 100))

    end_time = time.time()
    duration_ms = (end_time - start_time) * 1000
    memory_mb = get_memory_usage()
    
    response = {
        "duration_ms": duration_ms,
        "memory_mb": memory_mb,
        "cold_start": is_cold
    }
    
    is_cold = False
    
    return response

# AWS Lambda Entry Point
def lambda_handler(event, context):
    return handle(event, context)

# Azure Functions Entry Point (v1 model assumption, or adaptable)
def main(req):
    # For Azure, req is func.HttpRequest
    try:
        req_body = req.get_json()
    except ValueError:
        req_body = {}
    
    return json.dumps(handle(req_body, None))

# Google Cloud Functions Entry Point
def google_handler(request):
    request_json = request.get_json(silent=True)
    if request_json:
        return json.dumps(handle(request_json, None))
    else:
        return json.dumps(handle(request.args, None))
