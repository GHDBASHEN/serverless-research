import os
import shutil
import subprocess
import zipfile

def zip_dir(src_dir, zip_path):
    os.makedirs(os.path.dirname(zip_path), exist_ok=True)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                # Do not include build output directories in NodeJS/Python
                if "files" in root or "bin" in root or "target" in root:
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, src_dir)
                zipf.write(file_path, arcname)

if __name__ == "__main__":
    aws_tf_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(aws_tf_dir)))
    
    # 1. Compile Java and build JAR for AWS Lambda
    java_root = os.path.join(base_dir, 'benchmarks', 'java')
    java_src = os.path.join(java_root, 'src', 'main', 'java', 'com', 'serverless', 'benchmark', 'Function.java')
    bin_dir = os.path.join(aws_tf_dir, 'bin')
    target_dir = os.path.join(java_root, 'target')
    jar_path = os.path.join(target_dir, 'benchmark-1.0.jar')
    
    # Clean up previous build directories
    if os.path.exists(bin_dir):
        shutil.rmtree(bin_dir)
    os.makedirs(bin_dir, exist_ok=True)
    os.makedirs(target_dir, exist_ok=True)
    
    print("Compiling Java benchmark core...")
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
        
    # Clean up bin dir
    shutil.rmtree(bin_dir)
    
    # 2. Package Python zip
    python_src = os.path.join(base_dir, 'benchmarks', 'python')
    python_zip = os.path.join(aws_tf_dir, 'files', 'python.zip')
    zip_dir(python_src, python_zip)
    print(f"Zipped Python source to {python_zip}")
    
    # 3. Package Node.js zip
    nodejs_src = os.path.join(base_dir, 'benchmarks', 'nodejs')
    nodejs_zip = os.path.join(aws_tf_dir, 'files', 'nodejs.zip')
    zip_dir(nodejs_src, nodejs_zip)
    print(f"Zipped Node.js source to {nodejs_zip}")
