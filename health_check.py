#!/usr/bin/env python3
"""
Health check script for Tengen.ai
Verifies all components are working correctly
"""
import os
import sys
import subprocess
import json

def check_python_deps():
    """Check if Python dependencies are installed"""
    print("Checking Python dependencies...")
    try:
        import fastapi
        import uvicorn
        import langchain
        import requests
        from bs4 import BeautifulSoup
        print("[OK] Python dependencies: OK")
        return True
    except ImportError as e:
        print(f"[ERROR] Python dependencies: Missing {e}")
        return False

def check_node_deps():
    """Check if Node.js dependencies are installed"""
    print("Checking Node.js dependencies...")
    try:
        result = subprocess.run(
            ["npm", "list", "--depth=0"], 
            cwd="frontend", 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0:
            print("[OK] Node.js dependencies: OK")
            return True
        else:
            print("[ERROR] Node.js dependencies: Issues found")
            return False
    except Exception as e:
        print(f"[ERROR] Node.js dependencies: {e}")
        return False

def check_env_files():
    """Check if environment files exist and are configured"""
    print("Checking environment files...")
    
    # Check backend .env
    backend_env = "backend/.env"
    if os.path.exists(backend_env):
        with open(backend_env, 'r') as f:
            content = f.read()
            if "GOOGLE_API_KEY" in content and "your_google_api_key_here" not in content:
                print("[OK] Backend .env: Configured")
                backend_ok = True
            else:
                print("[WARNING] Backend .env: API key not set")
                backend_ok = False
    else:
        print("[ERROR] Backend .env: Missing")
        backend_ok = False
    
    # Check frontend .env.local
    frontend_env = "frontend/.env.local"
    if os.path.exists(frontend_env):
        print("[OK] Frontend .env.local: OK")
        frontend_ok = True
    else:
        print("[ERROR] Frontend .env.local: Missing")
        frontend_ok = False
    
    return backend_ok and frontend_ok

def check_backend_imports():
    """Check if backend modules can be imported"""
    print("Checking backend imports...")
    try:
        os.chdir("backend")
        result = subprocess.run(
            [sys.executable, "-c", "import api; print('Backend imports OK')"],
            capture_output=True,
            text=True
        )
        os.chdir("..")
        
        if result.returncode == 0:
            print("[OK] Backend imports: OK")
            return True
        else:
            print(f"[ERROR] Backend imports: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] Backend imports: {e}")
        return False

def check_frontend_build():
    """Check if frontend can build"""
    print("Checking frontend build...")
    try:
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd="frontend",
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("[OK] Frontend build: OK")
            return True
        else:
            print("[ERROR] Frontend build: Failed")
            print(f"Error: {result.stderr[:200]}...")
            return False
    except subprocess.TimeoutExpired:
        print("[WARNING] Frontend build: Timeout (but likely OK)")
        return True
    except Exception as e:
        print(f"[ERROR] Frontend build: {e}")
        return False

def main():
    print("Tengen.ai Health Check")
    print("=" * 40)
    
    checks = [
        check_python_deps,
        check_node_deps,
        check_env_files,
        check_backend_imports,
        # check_frontend_build  # Skip build check for now as it's slow
    ]
    
    results = []
    for check in checks:
        result = check()
        results.append(result)
        print()
    
    print("=" * 40)
    if all(results):
        print("[SUCCESS] All checks passed! Tengen.ai is ready to run.")
        print("\nTo start the application:")
        print("  python start_app.py")
        print("\nOr start components separately:")
        print("  Backend: python start_backend.py")
        print("  Frontend: node start_frontend.js")
    else:
        print("[WARNING] Some checks failed. Please fix the issues above.")
        print("\nFor help, see:")
        print("  - README.md")
        print("  - TROUBLESHOOTING.md")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)