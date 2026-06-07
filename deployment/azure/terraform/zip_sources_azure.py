import os
import shutil
import json
import subprocess
import zipfile

def create_zip(source_dir, output_zip):
    os.makedirs(os.path.dirname(output_zip), exist_ok=True)
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)

if __name__ == "__main__":
    azure_tf_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(azure_tf_dir)))
    temp_dir = os.path.join(azure_tf_dir, "temp_build")
    
    # Reset temp build directory
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    
    memories = [128, 256, 512, 1024, 2048]
    
    # 1. Package Python
    py_temp = os.path.join(temp_dir, "python")
    os.makedirs(py_temp, exist_ok=True)
    # Copy code files
    shutil.copy(os.path.join(base_dir, "benchmarks", "python", "handler.py"), py_temp)
    shutil.copy(os.path.join(base_dir, "benchmarks", "python", "main.py"), py_temp)
    shutil.copy(os.path.join(base_dir, "benchmarks", "python", "requirements.txt"), py_temp)
    
    for mem in memories:
        func_name = f"py_{mem}"
        func_dir = os.path.join(py_temp, func_name)
        os.makedirs(func_dir, exist_ok=True)
        function_json = {
            "scriptFile": "../handler.py",
            "entryPoint": "main",
            "bindings": [
                {
                    "authLevel": "anonymous",
                    "type": "httpTrigger",
                    "direction": "in",
                    "name": "req",
                    "methods": ["post"]
                },
                {
                    "type": "http",
                    "direction": "out",
                    "name": "$return"
                }
            ]
        }
        with open(os.path.join(func_dir, "function.json"), "w") as f:
            json.dump(function_json, f, indent=2)
            
    py_zip = os.path.join(azure_tf_dir, "files", "python.zip")
    create_zip(py_temp, py_zip)
    print(f"Zipped Python for Azure to {py_zip}")
    
    # 2. Package Node.js
    node_temp = os.path.join(temp_dir, "nodejs")
    os.makedirs(node_temp, exist_ok=True)
    # Copy code files
    shutil.copy(os.path.join(base_dir, "benchmarks", "nodejs", "index.js"), node_temp)
    shutil.copy(os.path.join(base_dir, "benchmarks", "nodejs", "package.json"), node_temp)
    
    for mem in memories:
        func_name = f"node_{mem}"
        func_dir = os.path.join(node_temp, func_name)
        os.makedirs(func_dir, exist_ok=True)
        function_json = {
            "scriptFile": "../index.js",
            "entryPoint": "main",
            "bindings": [
                {
                    "authLevel": "anonymous",
                    "type": "httpTrigger",
                    "direction": "in",
                    "name": "req",
                    "methods": ["post"]
                },
                {
                    "type": "http",
                    "direction": "out",
                    "name": "res"
                }
            ]
        }
        with open(os.path.join(func_dir, "function.json"), "w") as f:
            json.dump(function_json, f, indent=2)
            
    node_zip = os.path.join(azure_tf_dir, "files", "nodejs.zip")
    create_zip(node_temp, node_zip)
    print(f"Zipped Node.js for Azure to {node_zip}")
    
    # 3. Compile Java and Package Java
    java_root = os.path.join(base_dir, 'benchmarks', 'java')
    java_src = os.path.join(java_root, 'src', 'main', 'java', 'com', 'serverless', 'benchmark', 'Function.java')
    bin_dir = os.path.join(azure_tf_dir, 'bin')
    target_dir = os.path.join(java_root, 'target')
    jar_path = os.path.join(target_dir, 'benchmark-1.0.jar')
    
    if os.path.exists(bin_dir):
        shutil.rmtree(bin_dir)
    os.makedirs(bin_dir, exist_ok=True)
    os.makedirs(target_dir, exist_ok=True)
    
    print("Compiling Java benchmark core for Azure...")
    javac_cmd = ["javac", "-d", bin_dir, java_src]
    try:
        subprocess.run(javac_cmd, check=True)
        print("Java compilation successful.")
    except Exception as e:
        print(f"Error compiling Java: {e}")
        exit(1)
        
    print("Packaging compiled Java to JAR...")
    jar_cmd = ["jar", "cf", jar_path, "-C", bin_dir, "com"]
    try:
        subprocess.run(jar_cmd, check=True)
        print(f"Java JAR built successfully at {jar_path}")
    except Exception as e:
        print(f"Error building JAR: {e}")
        exit(1)
        
    shutil.rmtree(bin_dir)
    
    java_temp = os.path.join(temp_dir, "java")
    os.makedirs(java_temp, exist_ok=True)
    # Copy JAR to target folder inside the zip root
    zip_target = os.path.join(java_temp, "target")
    os.makedirs(zip_target, exist_ok=True)
    shutil.copy(jar_path, zip_target)
    
    for mem in memories:
        func_name = f"java_{mem}"
        func_dir = os.path.join(java_temp, func_name)
        os.makedirs(func_dir, exist_ok=True)
        function_json = {
            "scriptFile": "../target/benchmark-1.0.jar",
            "entryPoint": "com.serverless.benchmark.Function.handleRequest",
            "bindings": [
                {
                    "authLevel": "anonymous",
                    "type": "httpTrigger",
                    "direction": "in",
                    "name": "req",
                    "methods": ["post"]
                },
                {
                    "type": "http",
                    "direction": "out",
                    "name": "$return"
                }
            ]
        }
        with open(os.path.join(func_dir, "function.json"), "w") as f:
            json.dump(function_json, f, indent=2)
            
    java_zip = os.path.join(azure_tf_dir, "files", "java.zip")
    create_zip(java_temp, java_zip)
    print(f"Zipped Java for Azure to {java_zip}")
    
    # Clean up temp builds
    shutil.rmtree(temp_dir)
    print("Cleaned up temporary build directories.")
