#!/usr/bin/env python3
"""
Simple startup script for Tengen.ai
Starts both backend and frontend servers
"""
import subprocess
import sys
import time
import threading
import os

def start_backend():
    """Start the backend server"""
    print("🚀 Starting backend server...")
    try:
        os.chdir("backend")
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped")
    except Exception as e:
        print(f"❌ Backend error: {e}")

def start_frontend():
    """Start the frontend server"""
    print("🚀 Starting frontend server...")
    try:
        time.sleep(3)  # Give backend time to start
        os.chdir("../frontend")
        subprocess.run(["npm", "run", "dev"])
    except KeyboardInterrupt:
        print("\n🛑 Frontend server stopped")
    except Exception as e:
        print(f"❌ Frontend error: {e}")

def main():
    print("🔬 Starting Tengen.ai Research Assistant")
    print("=" * 50)
    print("📍 Backend API: http://localhost:8000")
    print("📍 Frontend UI: http://localhost:3000")
    print("📍 API Docs: http://localhost:8000/docs")
    print("=" * 50)
    print("Press Ctrl+C to stop all servers")
    print("=" * 50)
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Start frontend (this will block)
    try:
        start_frontend()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Tengen.ai...")
        print("👋 Thank you for using Tengen.ai!")

if __name__ == "__main__":
    main()