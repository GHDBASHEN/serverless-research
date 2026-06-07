import os
import re
import textwrap

BENCHMARKS_DIR = r'd:\Projects\Research\serverless-research\benchmarks'
HANDLER_FILE = r'd:\Projects\Research\serverless-research\benchmarks\python\handler.py'

WORKLOADS = {
    'micro': {
        'cpu_intensive': [
            'fibonacci', 'matrix_mult', 'prime_sieve', 'float_ops',
            'cpu_math_1', 'cpu_math_2', 'cpu_math_3', 'cpu_math_4', 'cpu_math_5'
        ],
        'memory_intensive': [
            'mem_alloc_1', 'mem_alloc_2', 'mem_alloc_3', 'mem_string_4', 'mem_dict_5'
        ],
        'io_intensive': [
            'file_io', 'disk_io_1', 'disk_io_2', 'disk_io_3', 'disk_io_4', 'disk_io_5'
        ],
        'network_intensive': [
            'net_sim_1', 'net_sim_2', 'net_sim_3', 'net_sim_4', 'net_sim_5'
        ]
    },
    'macro': {
        'data_processing': [
            'json_transform', 'data_proc_1', 'data_proc_2', 'data_proc_3', 'data_proc_4', 'data_proc_5'
        ],
        'crypto_hashing': [
            'crypto_hash', 'crypto_1', 'crypto_2', 'crypto_3', 'crypto_4', 'crypto_5'
        ],
        'web_business': [
            'web_biz_1', 'web_biz_2', 'web_biz_3', 'web_biz_4', 'web_biz_5'
        ],
        'scientific_computing': [
            'sci_1', 'sci_2', 'sci_3', 'sci_4', 'sci_5'
        ]
    }
}

TEMPLATE = """\
# {category}/{subcategory}/{workload}.py
import json
import time
import math
import random
import os

def handle(event, context):
    \"\"\"
    Standalone implementation for the '{workload}' benchmark.
    Category: {category} -> {subcategory}
    \"\"\"
    start_time = time.time()
    
    # Parse input
    payload = event
    if isinstance(event, str):
        try: payload = json.loads(event)
        except: pass
        
    size = int(payload.get('size', 100))
    result = None
    
{logic_block}
    
    duration_ms = (time.time() - start_time) * 1000
    
    return {{
        'statusCode': 200,
        'body': json.dumps({{
            'workload': '{workload}',
            'size': size,
            'result': str(result)[:500], # Trim large results for response
            'duration_ms': duration_ms
        }})
    }}
"""

def extract_logic_from_handler():
    with open(HANDLER_FILE, 'r') as f:
        content = f.read()

    # Find the main if/elif block
    # It starts with "if workload == 'fibonacci':"
    blocks = {}
    
    lines = content.splitlines()
    current_workload = None
    current_lines = []
    
    for line in lines:
        match = re.match(r"^\s*(?:elif|if)\s+workload\s*==\s*['\"]([^'\"]+)['\"]:", line)
        if match:
            if current_workload:
                blocks[current_workload] = current_lines
            current_workload = match.group(1)
            current_lines = []
        elif current_workload:
            # Check if we hit the end of the handler function
            if line.strip() == "duration_ms = (time.time() - start_time) * 1000" or line.strip() == "return result":
                blocks[current_workload] = current_lines
                current_workload = None
            else:
                current_lines.append(line)
                
    if current_workload:
        blocks[current_workload] = current_lines

    return blocks

def main():
    print("Extracting real logic from handler.py...")
    logic_blocks = extract_logic_from_handler()
    
    count = 0
    for category, subcategories in WORKLOADS.items():
        for subcategory, workloads in subcategories.items():
            dir_path = os.path.join(BENCHMARKS_DIR, category, subcategory)
            os.makedirs(dir_path, exist_ok=True)
            
            for workload in workloads:
                file_path = os.path.join(dir_path, f"{workload}.py")
                
                # Get logic block and adjust indentation
                raw_lines = logic_blocks.get(workload, ["        # Implementation missing in handler.py", f"        result = 'Missing {workload}'"])
                
                # The lines are indented by 8 spaces in handler.py (inside handle() -> if block).
                # In the standalone file, they will be inside handle(), so we want 4 spaces.
                # Actually, let's just textwrap.dedent and then indent by 4.
                raw_text = "\\n".join(raw_lines)
                dedented = textwrap.dedent(raw_text)
                indented = textwrap.indent(dedented, "    ")
                
                code = TEMPLATE.format(
                    category=category,
                    subcategory=subcategory,
                    workload=workload,
                    logic_block=indented
                )
                with open(file_path, 'w') as f:
                    f.write(code)
                count += 1
                
    print(f"Successfully populated {count} files with actual logic!")

if __name__ == "__main__":
    main()
