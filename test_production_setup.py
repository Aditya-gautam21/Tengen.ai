#!/usr/bin/env python3
"""
Production Setup Test Script
Verifies that the Tengen.ai production setup is working correctly
"""

import os
import sys
import requests
import json
import time
from datetime import datetime

def test_environment():
    """Test environment setup"""
    print("🔍 Testing environment setup...")
    
    # Check if API key is set
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_google_api_key_here":
        print("❌ GOOGLE_API_KEY not properly configured")
        return False
    
    print("✅ Environment variables configured")
    return True

def test_api_health(base_url="http://localhost:8080"):
    """Test API health endpoints"""
    print(f"🏥 Testing API health at {base_url}...")
    
    endpoints = [
        "/api/v1/health/live",
        "/api/v1/health/ready", 
        "/api/v1/health",
        "/api/v1/health/detailed"
    ]
    
    results = {}
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                results[endpoint] = "✅ Healthy"
                print(f"  ✅ {endpoint} - {response.status_code}")
            else:
                results[endpoint] = f"❌ HTTP {response.status_code}"
                print(f"  ❌ {endpoint} - {response.status_code}")
        except requests.exceptions.RequestException as e:
            results[endpoint] = f"❌ Connection error: {e}"
            print(f"  ❌ {endpoint} - Connection error")
    
    return results

def test_inference_endpoint(base_url="http://localhost:8080"):
    """Test inference endpoint"""
    print(f"🤖 Testing inference endpoint at {base_url}...")
    
    test_request = {
        "prompt": "Hello, how are you?",
        "request_type": "general"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/predict",
            json=test_request,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Inference successful - Status: {result.get('status')}")
            print(f"  ⏱️  Processing time: {result.get('processing_time', 0):.2f}s")
            return True
        else:
            print(f"  ❌ Inference failed - HTTP {response.status_code}")
            print(f"  📄 Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Inference error: {e}")
        return False

def test_logging_endpoint(base_url="http://localhost:8080"):
    """Test logging endpoint"""
    print(f"📝 Testing logging endpoint at {base_url}...")
    
    try:
        response = requests.get(f"{base_url}/api/v1/logs", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            log_count = len(result.get("logs", []))
            print(f"  ✅ Logs retrieved - {log_count} entries")
            return True
        else:
            print(f"  ❌ Logs retrieval failed - HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Logs error: {e}")
        return False

def test_docker_setup():
    """Test Docker setup"""
    print("🐳 Testing Docker setup...")
    
    try:
        import subprocess
        
        # Check if Docker is running
        result = subprocess.run(["docker", "ps"], capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✅ Docker is running")
            
            # Check if tengen container is running
            if "tengen" in result.stdout.lower():
                print("  ✅ Tengen container is running")
                return True
            else:
                print("  ⚠️  Tengen container not found (may not be started yet)")
                return False
        else:
            print("  ❌ Docker is not running or not installed")
            return False
            
    except FileNotFoundError:
        print("  ❌ Docker not found in PATH")
        return False
    except Exception as e:
        print(f"  ❌ Docker test error: {e}")
        return False

def generate_report(results):
    """Generate test report"""
    print("\n" + "="*60)
    print("📊 PRODUCTION SETUP TEST REPORT")
    print("="*60)
    print(f"Generated: {datetime.now().isoformat()}")
    print()
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if "✅" in str(result))
    
    print(f"Overall Status: {passed_tests}/{total_tests} tests passed")
    print()
    
    for test_name, result in results.items():
        print(f"{test_name}: {result}")
    
    print()
    if passed_tests == total_tests:
        print("🎉 All tests passed! Your production setup is ready.")
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
    
    return passed_tests == total_tests

def main():
    """Main test function"""
    print("🚀 Tengen.ai Production Setup Test")
    print("="*40)
    
    # Check if API URL is provided
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"
    print(f"Testing API at: {base_url}")
    print()
    
    results = {}
    
    # Run tests
    results["Environment Setup"] = test_environment()
    
    # Wait a moment for API to be ready
    print("⏳ Waiting for API to be ready...")
    time.sleep(2)
    
    health_results = test_api_health(base_url)
    results["API Health"] = "✅ All endpoints healthy" if all("✅" in str(r) for r in health_results.values()) else "❌ Some endpoints failed"
    
    results["Inference Endpoint"] = test_inference_endpoint(base_url)
    results["Logging Endpoint"] = test_logging_endpoint(base_url)
    results["Docker Setup"] = test_docker_setup()
    
    # Generate report
    success = generate_report(results)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
