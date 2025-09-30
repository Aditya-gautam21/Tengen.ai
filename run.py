#!/usr/bin/env python3
"""
Simple run script for Tengen.ai Chat Interface
"""
import subprocess
import sys
import time
import threading
import webbrowser
import os

def print_status():
    print("🚀 Tengen.ai Chat Interface")
    print("=" * 40)
    print("✅ Pure black background")
    print("✅ Lime green accents") 
    print("✅ Modern design")
    print("✅ Research capabilities")
    print("=" * 40)

def start_backend():
    """Start the FastAPI backend"""
    def run():
        try:
            print("🔧 Starting backend...")
            subprocess.run([sys.executable, "backend/app.py"])
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"Backend error: {e}")
    
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return thread

def start_frontend():
    """Start the Next.js frontend"""
    try:
        print("🎨 Starting frontend...")
        time.sleep(2)  # Wait for backend
        
        # Check if frontend directory exists
        if not os.path.exists("frontend"):
            print("❌ Frontend directory not found")
            return
        
        # Try npm commands
        npm_commands = ["npm", "npm.cmd"]
        
        for npm_cmd in npm_commands:
            try:
                # Install dependencies
                print(f"📦 Installing with {npm_cmd}...")
                subprocess.run([npm_cmd, "install", "--legacy-peer-deps"], 
                             cwd="frontend", check=True, capture_output=True)
                print("✅ Dependencies ready")
                
                # Start dev server
                print("🚀 Starting dev server...")
                subprocess.run([npm_cmd, "run", "dev"], cwd="frontend")
                break
            except FileNotFoundError:
                continue
            except subprocess.CalledProcessError as e:
                print(f"Error with {npm_cmd}: {e}")
                continue
        else:
            print("❌ npm not found")
            
    except KeyboardInterrupt:
        print("\n🛑 Stopped")
    except Exception as e:
        print(f"Error: {e}")

def open_browser():
    """Auto-open browser"""
    def delayed_open():
        time.sleep(6)
        try:
            webbrowser.open("http://localhost:3000")
            print("🌐 Opened http://localhost:3000")
        except:
            print("💡 Open http://localhost:3000 manually")
    
    threading.Thread(target=delayed_open, daemon=True).start()

def main():
    print_status()
    
    print("🌐 Access points:")
    print("📍 Chat: http://localhost:3000")
    print("📍 API: http://localhost:8000")
    print("\n💡 Press Ctrl+C to stop")
    print("=" * 40)
    
    try:
        # Start backend
        start_backend()
        
        # Auto-open browser
        open_browser()
        
        # Start frontend (this blocks)
        start_frontend()
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()