import os
import zipfile

def zip_dir(src_dir, zip_path):
    os.makedirs(os.path.dirname(zip_path), exist_ok=True)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, src_dir)
                zipf.write(file_path, arcname)

if __name__ == "__main__":
    # Locate base directories
    # zip_sources.py is in base/deployment/google/terraform/
    terraform_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(terraform_dir)))
    
    # 1. Zip Python
    python_src = os.path.join(base_dir, 'benchmarks', 'python')
    python_zip = os.path.join(terraform_dir, 'files', 'python.zip')
    zip_dir(python_src, python_zip)
    print(f"Zipped Python source to {python_zip}")
    
    # 2. Zip Node.js
    nodejs_src = os.path.join(base_dir, 'benchmarks', 'nodejs')
    nodejs_zip = os.path.join(terraform_dir, 'files', 'nodejs.zip')
    zip_dir(nodejs_src, nodejs_zip)
    print(f"Zipped Node.js source to {nodejs_zip}")
    
    # 3. Zip Java
    java_src = os.path.join(base_dir, 'benchmarks', 'java')
    java_zip = os.path.join(terraform_dir, 'files', 'java.zip')
    zip_dir(java_src, java_zip)
    print(f"Zipped Java source to {java_zip}")
