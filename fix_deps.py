#!/usr/bin/env python3
"""
Fix dependencies for Tengen.ai
"""
import subprocess
import sys

def install_package(package):
    """Install a Python package"""
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", package], 
                      check=True, capture_output=True)
        print(f"✅ Installed {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package}")
        return False

def main():
    print("🔧 Fixing Tengen.ai Dependencies")
    print("=" * 40)
    
    # Install the new huggingface package
    packages = [
        "langchain-huggingface",
        "sentence-transformers",
        "faiss-cpu"
    ]
    
    for package in packages:
        install_package(package)
    
    print("\n✅ Dependencies fixed!")
    print("💡 Now run: python start.py")

if __name__ == "__main__":
    main()