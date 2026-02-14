import json
import os

def generate():
    benchmarks = []
    
    # Configuration
    # 5 Algos * 5 Sizes * 4 Variations = 100 benchmarks
    
    algos = {
        'fibonacci': {
            'XS': [10, 11, 12, 13], 
            'S': [18, 19, 20, 21], 
            'M': [24, 25, 26, 27], 
            'L': [30, 31, 32, 33], 
            'XL': [34, 35, 36, 37]
        },
        'matrix_mult': {
            'XS': [10, 15, 20, 25],
            'S': [40, 45, 50, 55],
            'M': [80, 90, 100, 110],
            'L': [150, 175, 200, 225],
            'XL': [300, 350, 400, 450]
        },
        'prime_sieve': {
            'XS': [100, 200, 300, 400],
            'S': [1000, 1500, 2000, 2500],
            'M': [10000, 15000, 20000, 25000],
            'L': [100000, 150000, 200000, 250000],
            'XL': [1000000, 1250000, 1500000, 1750000]
        },
        'file_io': { # Bytes
            'XS': [100, 200, 300, 400],
            'S': [1024, 2048, 4096, 8192],
            'M': [10240, 20480, 50000, 100000],
            'L': [1048576, 1500000, 2000000, 2500000], # 1-2.5 MB
            'XL': [5000000, 7500000, 10000000, 12500000] # 5-12 MB
        },
        'float_ops': {
            'XS': [1000, 2000, 3000, 4000],
            'S': [50000, 60000, 70000, 80000],
            'M': [500000, 750000, 1000000, 1250000],
            'L': [5000000, 7500000, 10000000, 12500000],
            'XL': [20000000, 30000000, 40000000, 50000000]
        }
    }
    
    id_counter = 1
    
    for algo, sizes in algos.items():
        for size_label, values in sizes.items():
            for i, val in enumerate(values):
                benchmarks.append({
                    "id": id_counter,
                    "name": f"{algo}_{size_label.lower()}_v{i+1}",
                    "payload": {
                        "workload": algo,
                        "size": val
                    },
                    "category": size_label
                })
                id_counter += 1
                
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'experimentation', 'benchmarks.json')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(benchmarks, f, indent=2)
        
    print(f"Generated {len(benchmarks)} benchmarks to {output_path}")

if __name__ == "__main__":
    generate()
