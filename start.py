#!/usr/bin/env python3
"""
Simple startup script for Tengen.ai
"""
import subprocess
import sys
import time
import threading
import os
from pathlib import Path

def print_info():
    print("🚀 Tengen.ai Chat Interface")
    print("=" * 40)
    print("✅ Modern black design")
    print("✅ Lime green accents")
    print("✅ AI research capabilities")
    print("=" * 40)

def start_backend():
    """Start backend in thread"""
    def run():
        try:
            print("🔧 Starting backend...")
            subprocess.run([sys.executable, "backend/app.py"])
        except KeyboardInterrupt:
            pass
    
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return thread

def start_frontend():
    """Start frontend"""
    print("🎨 Starting frontend...")
    time.sleep(3)  # Wait for backend
    
    # Check frontend exists
    if not Path("frontend").exists():
        print("❌ Frontend directory not found")
        return
    
    # Try npm commands
    npm_commands = ["npm", "npm.cmd"]
    
    for npm_cmd in npm_commands:
        try:
            # Install deps
            print(f"📦 Installing dependencies...")
            result = subprocess.run([npm_cmd, "install", "--legacy-peer-deps"], 
                                  cwd="frontend", capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Warning: {result.stderr}")
            else:
                print("✅ Dependencies installed")
            
            # Start dev server
            print("🚀 Starting chat interface...")
            subprocess.run([npm_cmd, "run", "dev"], cwd="frontend")
            break
            
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"Error: {e}")
            continue
    else:
        print("❌ npm not found - install Node.js")

def main():
    print_info()
    
    print("🌐 Will be available at:")
    print("📍 http://localhost:3000")
    print("📍 Backend: http://localhost:8000")
    print("\n💡 Press Ctrl+C to stop")
    print("=" * 40)
    
    try:
        # Start backend
        start_backend()
        
        # Start frontend
        start_frontend()
        
    except KeyboardInterrupt:
        print("\n👋 Stopped!")

if __name__ == "__main__":
    main()