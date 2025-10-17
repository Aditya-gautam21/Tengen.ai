"""
Performance Monitoring
Monitor API performance metrics and generate reports
"""

import requests
import time
import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor API performance metrics"""
    
    def __init__(self, api_url: str):
        self.api_url = api_url.rstrip('/')
        self.metrics = {
            "response_times": [],
            "success_rates": [],
            "error_counts": [],
            "throughput": []
        }
        self.test_requests = [
            {"endpoint": "/api/v1/health/live", "method": "GET"},
            {"endpoint": "/api/v1/predict", "method": "POST", "data": {"prompt": "Hello", "request_type": "general"}},
            {"endpoint": "/api/v1/health/detailed", "method": "GET"}
        ]
    
    def measure_endpoint_performance(self, endpoint: str, method: str = "GET", data: Dict = None, iterations: int = 10) -> Dict[str, Any]:
        """Measure performance of a single endpoint"""
        response_times = []
        success_count = 0
        error_count = 0
        
        logger.info(f"Measuring performance for {method} {endpoint}")
        
        for i in range(iterations):
            start_time = time.time()
            
            try:
                if method.upper() == "GET":
                    response = requests.get(f"{self.api_url}{endpoint}", timeout=30)
                elif method.upper() == "POST":
                    response = requests.post(f"{self.api_url}{endpoint}", json=data, timeout=30)
                
                response_time = time.time() - start_time
                response_times.append(response_time)
                
                if response.status_code == 200:
                    success_count += 1
                else:
                    error_count += 1
                    logger.warning(f"Request {i+1} failed with status {response.status_code}")
                
            except requests.exceptions.RequestException as e:
                error_count += 1
                logger.error(f"Request {i+1} failed: {e}")
            
            # Small delay between requests
            time.sleep(0.1)
        
        # Calculate statistics
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            median_response_time = statistics.median(response_times)
            
            # Calculate percentiles
            sorted_times = sorted(response_times)
            p95 = sorted_times[int(len(sorted_times) * 0.95)] if len(sorted_times) > 0 else 0
            p99 = sorted_times[int(len(sorted_times) * 0.99)] if len(sorted_times) > 0 else 0
        else:
            avg_response_time = min_response_time = max_response_time = median_response_time = p95 = p99 = 0
        
        success_rate = (success_count / iterations) * 100 if iterations > 0 else 0
        
        return {
            "endpoint": endpoint,
            "method": method,
            "iterations": iterations,
            "success_count": success_count,
            "error_count": error_count,
            "success_rate": success_rate,
            "response_times": {
                "average": avg_response_time,
                "minimum": min_response_time,
                "maximum": max_response_time,
                "median": median_response_time,
                "p95": p95,
                "p99": p99,
                "raw_times": response_times
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def run_comprehensive_test(self, iterations_per_endpoint: int = 10) -> Dict[str, Any]:
        """Run comprehensive performance test"""
        logger.info("Starting comprehensive performance test...")
        
        results = []
        total_start_time = time.time()
        
        for test_request in self.test_requests:
            result = self.measure_endpoint_performance(
                test_request["endpoint"],
                test_request["method"],
                test_request.get("data"),
                iterations_per_endpoint
            )
            results.append(result)
        
        total_end_time = time.time()
        total_duration = total_end_time - total_start_time
        
        # Calculate overall metrics
        all_response_times = []
        total_success = 0
        total_errors = 0
        total_requests = 0
        
        for result in results:
            all_response_times.extend(result["response_times"]["raw_times"])
            total_success += result["success_count"]
            total_errors += result["error_count"]
            total_requests += result["iterations"]
        
        overall_metrics = {
            "test_duration": total_duration,
            "total_requests": total_requests,
            "total_success": total_success,
            "total_errors": total_errors,
            "overall_success_rate": (total_success / total_requests) * 100 if total_requests > 0 else 0,
            "overall_response_times": {
                "average": statistics.mean(all_response_times) if all_response_times else 0,
                "minimum": min(all_response_times) if all_response_times else 0,
                "maximum": max(all_response_times) if all_response_times else 0,
                "median": statistics.median(all_response_times) if all_response_times else 0,
                "p95": sorted(all_response_times)[int(len(all_response_times) * 0.95)] if all_response_times else 0,
                "p99": sorted(all_response_times)[int(len(all_response_times) * 0.99)] if all_response_times else 0
            },
            "throughput": total_requests / total_duration if total_duration > 0 else 0,
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "overall_metrics": overall_metrics,
            "endpoint_results": results,
            "test_configuration": {
                "iterations_per_endpoint": iterations_per_endpoint,
                "test_requests": self.test_requests
            }
        }
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a human-readable performance report"""
        overall = results["overall_metrics"]
        
        report = f"""
# Tengen.ai Performance Report
Generated: {overall['timestamp']}

## Overall Performance
- **Test Duration**: {overall['test_duration']:.2f} seconds
- **Total Requests**: {overall['total_requests']}
- **Success Rate**: {overall['overall_success_rate']:.2f}%
- **Throughput**: {overall['throughput']:.2f} requests/second

## Response Time Statistics
- **Average**: {overall['overall_response_times']['average']:.3f}s
- **Minimum**: {overall['overall_response_times']['minimum']:.3f}s
- **Maximum**: {overall['overall_response_times']['maximum']:.3f}s
- **Median**: {overall['overall_response_times']['median']:.3f}s
- **95th Percentile**: {overall['overall_response_times']['p95']:.3f}s
- **99th Percentile**: {overall['overall_response_times']['p99']:.3f}s

## Endpoint Performance
"""
        
        for result in results["endpoint_results"]:
            report += f"""
### {result['method']} {result['endpoint']}
- **Success Rate**: {result['success_rate']:.2f}%
- **Average Response Time**: {result['response_times']['average']:.3f}s
- **95th Percentile**: {result['response_times']['p95']:.3f}s
- **Errors**: {result['error_count']}/{result['iterations']}
"""
        
        return report
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """Save performance test results"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"performance_test_{timestamp}.json"
        
        filepath = f"monitoring/{filename}"
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Performance results saved to {filepath}")
        
        # Also save human-readable report
        report_filename = filename.replace('.json', '.md')
        report_filepath = f"monitoring/{report_filename}"
        
        with open(report_filepath, 'w') as f:
            f.write(self.generate_report(results))
        
        logger.info(f"Performance report saved to {report_filepath}")

def main():
    """Main function for running performance tests"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Tengen.ai Performance Monitor")
    parser.add_argument("--api-url", default="http://localhost:8080", help="API base URL")
    parser.add_argument("--iterations", type=int, default=10, help="Iterations per endpoint")
    parser.add_argument("--output", help="Output filename")
    
    args = parser.parse_args()
    
    monitor = PerformanceMonitor(args.api_url)
    
    # Run performance test
    results = monitor.run_comprehensive_test(args.iterations)
    
    # Print summary
    overall = results["overall_metrics"]
    print(f"\nPerformance Test Results:")
    print(f"Success Rate: {overall['overall_success_rate']:.2f}%")
    print(f"Average Response Time: {overall['overall_response_times']['average']:.3f}s")
    print(f"Throughput: {overall['throughput']:.2f} requests/second")
    
    # Save results
    monitor.save_results(results, args.output)

if __name__ == "__main__":
    main()
