#!/usr/bin/env python3
"""
Tengen.ai - AI Research Assistant
One-click startup script
"""
import subprocess
import sys
import time
import threading
import webbrowser
import os
from pathlib import Path

def print_banner():
    banner = """
    ████████╗███████╗███╗   ██╗ ██████╗ ███████╗███╗   ██╗   █████╗ ██╗
    ╚══██╔══╝██╔════╝████╗  ██║██╔════╝ ██╔════╝████╗  ██║  ██╔══██╗██║
       ██║   █████╗  ██╔██╗ ██║██║  ███╗█████╗  ██╔██╗ ██║  ███████║██║
       ██║   ██╔══╝  ██║╚██╗██║██║   ██║██╔══╝  ██║╚██╗██║  ██╔══██║██║
       ██║   ███████╗██║ ╚████║╚██████╔╝███████╗██║ ╚████║██╗██║  ██║██║
       ╚═╝   ╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚═╝╚═╝  ╚═╝╚═╝
    
    🤖 AI Research Assistant - Modern Chat Interface
    """
    print(banner)

def check_environment():
    """Check if environment is set up"""
    env_file = Path("backend/.env")
    if not env_file.exists():
        print("⚠️  Creating backend/.env file...")
        with open(env_file, 'w') as f:
            f.write("GOOGLE_API_KEY=your_google_api_key_here\n")
        print("❌ Please edit backend/.env and add your Google Gemini API key")
        print("💡 Get your key from: https://makersuite.google.com/app/apikey")
        return False
    
    with open(env_file, 'r') as f:
        content = f.read()
        if "your_google_api_key_here" in content:
            print("❌ Please set your Google API key in backend/.env")
            return False
    
    return True

def install_dependencies():
    """Install Python and Node.js dependencies"""
    print("📦 Installing dependencies...")
    
    # Python dependencies
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Python dependencies installed")
    except subprocess.CalledProcessError:
        print("❌ Failed to install Python dependencies")
        return False
    
    # Node.js dependencies
    npm_commands = ["npm", "npm.cmd"]
    for npm_cmd in npm_commands:
        try:
            subprocess.run([npm_cmd, "install", "--legacy-peer-deps"], 
                         cwd="frontend", check=True, capture_output=True)
            print("✅ Node.js dependencies installed")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    print("❌ Failed to install Node.js dependencies")
    return False

def start_backend():
    """Start backend server"""
    def run_backend():
        try:
            print("🚀 Starting backend server...")
            subprocess.run([sys.executable, "backend/app.py"])
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"Backend error: {e}")
    
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    return backend_thread

def start_frontend():
    """Start frontend"""
    try:
        print("🎨 Starting frontend...")
        time.sleep(3)  # Give backend time to start
        
        npm_commands = ["npm", "npm.cmd"]
        for npm_cmd in npm_commands:
            try:
                subprocess.run([npm_cmd, "run", "dev"], cwd="frontend")
                break
            except FileNotFoundError:
                continue
        else:
            print("❌ Could not start frontend - npm not found")
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        print(f"Frontend error: {e}")

def open_browser():
    """Open browser after delay"""
    def delayed_open():
        time.sleep(8)
        try:
            ports = [3000, 3001, 3002]
            for port in ports:
                try:
                    import requests
                    response = requests.get(f"http://localhost:{port}", timeout=2)
                    if response.status_code == 200:
                        print(f"🌐 Opening http://localhost:{port}")
                        webbrowser.open(f"http://localhost:{port}")
                        return
                except:
                    continue
            print("💡 Please open http://localhost:3000 manually")
        except ImportError:
            print("💡 Please open http://localhost:3000 manually")
    
    threading.Thread(target=delayed_open, daemon=True).start()

def main():
    print_banner()
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    print("\n" + "="*60)
    print("🚀 Starting Tengen.ai Research Assistant")
    print("="*60)
    print("📍 Chat Interface: http://localhost:3000")
    print("📍 Backend API: http://localhost:8000")
    print("📍 API Docs: http://localhost:8000/docs")
    print("="*60)
    print("💡 Press Ctrl+C to stop all servers")
    print("="*60)
    
    try:
        # Start backend
        start_backend()
        
        # Auto-open browser
        open_browser()
        
        # Start frontend (blocks)
        start_frontend()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Tengen.ai...")
        print("👋 Thank you for using Tengen.ai!")

if __name__ == "__main__":
    main()