#!/usr/bin/env python3
"""
Quick test for the chat interface
"""
import requests
import time

def test_backend():
    """Test if backend is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend is running")
            print(f"   Status: {data.get('status')}")
            print(f"   Google API: {data.get('google_api_configured')}")
            return True
        else:
            print("❌ Backend not responding")
            return False
    except requests.exceptions.RequestException:
        print("❌ Backend not running")
        return False

def test_frontend():
    """Test if frontend is running"""
    ports = [3000, 3001, 3002]
    for port in ports:
        try:
            response = requests.get(f"http://localhost:{port}", timeout=3)
            if response.status_code == 200:
                print(f"✅ Frontend running on port {port}")
                return port
        except requests.exceptions.RequestException:
            continue
    
    print("❌ Frontend not running")
    return None

def main():
    print("🧪 Testing Tengen.ai Chat Interface")
    print("=" * 40)
    
    # Test backend
    backend_ok = test_backend()
    
    # Test frontend
    frontend_port = test_frontend()
    
    print("\n📋 Test Results:")
    print(f"Backend: {'✅' if backend_ok else '❌'}")
    print(f"Frontend: {'✅' if frontend_port else '❌'}")
    
    if backend_ok and frontend_port:
        print(f"\n🎉 Everything is working!")
        print(f"🌐 Open: http://localhost:{frontend_port}")
    else:
        print(f"\n⚠️  Some services are not running")
        print("💡 Run: python run.py")

if __name__ == "__main__":
    main()