"""
Uptime Monitoring Script
Simple monitoring script for checking API health
"""

import requests
import time
import json
import logging
from datetime import datetime
from typing import Dict, Any
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UptimeMonitor:
    """Simple uptime monitoring for Tengen.ai API"""
    
    def __init__(self, api_url: str, check_interval: int = 60):
        self.api_url = api_url.rstrip('/')
        self.check_interval = check_interval
        self.health_endpoints = [
            "/api/v1/health/live",
            "/api/v1/health/ready",
            "/api/v1/health/detailed"
        ]
        self.results = []
    
    def check_endpoint(self, endpoint: str) -> Dict[str, Any]:
        """Check a single endpoint"""
        url = f"{self.api_url}{endpoint}"
        start_time = time.time()
        
        try:
            response = requests.get(url, timeout=10)
            response_time = time.time() - start_time
            
            return {
                "endpoint": endpoint,
                "status": "success" if response.status_code == 200 else "failed",
                "status_code": response.status_code,
                "response_time": response_time,
                "timestamp": datetime.now().isoformat(),
                "error": None
            }
            
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            return {
                "endpoint": endpoint,
                "status": "error",
                "status_code": None,
                "response_time": response_time,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def run_health_check(self) -> Dict[str, Any]:
        """Run comprehensive health check"""
        logger.info("Starting health check...")
        
        results = []
        for endpoint in self.health_endpoints:
            result = self.check_endpoint(endpoint)
            results.append(result)
            
            if result["status"] == "success":
                logger.info(f"✅ {endpoint} - {result['response_time']:.2f}s")
            else:
                logger.error(f"❌ {endpoint} - {result['error']}")
        
        # Overall status
        overall_status = "healthy" if all(r["status"] == "success" for r in results) else "unhealthy"
        
        health_summary = {
            "overall_status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "endpoints": results,
            "total_endpoints": len(self.health_endpoints),
            "successful_endpoints": len([r for r in results if r["status"] == "success"])
        }
        
        self.results.append(health_summary)
        return health_summary
    
    def save_results(self, filename: str = None):
        """Save monitoring results to file"""
        if filename is None:
            filename = f"uptime_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = os.path.join("monitoring", filename)
        os.makedirs("monitoring", exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"Results saved to {filepath}")
    
    def run_continuous_monitoring(self, duration_hours: int = 24):
        """Run continuous monitoring for specified duration"""
        logger.info(f"Starting continuous monitoring for {duration_hours} hours...")
        
        start_time = time.time()
        end_time = start_time + (duration_hours * 3600)
        
        while time.time() < end_time:
            try:
                health_summary = self.run_health_check()
                
                # Log summary
                logger.info(f"Health check completed: {health_summary['successful_endpoints']}/{health_summary['total_endpoints']} endpoints healthy")
                
                # Save results every hour
                if len(self.results) % 60 == 0:  # Assuming 1-minute intervals
                    self.save_results()
                
                # Wait for next check
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(self.check_interval)
        
        # Save final results
        self.save_results()
        logger.info("Monitoring completed")

def main():
    """Main function for running uptime monitoring"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Tengen.ai Uptime Monitor")
    parser.add_argument("--api-url", default="http://localhost:8080", help="API base URL")
    parser.add_argument("--interval", type=int, default=60, help="Check interval in seconds")
    parser.add_argument("--duration", type=int, default=1, help="Monitoring duration in hours")
    parser.add_argument("--single-check", action="store_true", help="Run single health check")
    
    args = parser.parse_args()
    
    monitor = UptimeMonitor(args.api_url, args.interval)
    
    if args.single_check:
        result = monitor.run_health_check()
        print(json.dumps(result, indent=2))
    else:
        monitor.run_continuous_monitoring(args.duration)

if __name__ == "__main__":
    main()
