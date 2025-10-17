# Monitoring & Observability

This directory contains monitoring tools and scripts for Tengen.ai production deployment.

## Tools

### 1. Uptime Monitor (`uptime_monitor.py`)

Simple uptime monitoring script that checks API health endpoints.

**Usage:**
```bash
# Single health check
python monitoring/uptime_monitor.py --single-check

# Continuous monitoring for 1 hour
python monitoring/uptime_monitor.py --duration 1

# Custom API URL and interval
python monitoring/uptime_monitor.py --api-url https://api.tengen.ai --interval 30
```

**Features:**
- Checks multiple health endpoints
- Configurable check intervals
- Saves results to JSON files
- Continuous monitoring mode

### 2. Performance Monitor (`performance_monitor.py`)

Comprehensive performance testing tool that measures API response times, success rates, and throughput.

**Usage:**
```bash
# Basic performance test
python monitoring/performance_monitor.py

# Custom iterations and output file
python monitoring/performance_monitor.py --iterations 20 --output my_test.json

# Test against production API
python monitoring/performance_monitor.py --api-url https://api.tengen.ai
```

**Features:**
- Measures response times (avg, min, max, percentiles)
- Calculates success rates and error counts
- Generates throughput metrics
- Creates human-readable reports
- Saves detailed JSON results

## Monitoring Setup

### Production Monitoring

For production deployments, consider integrating with:

1. **AWS CloudWatch**
   - Custom metrics for response times
   - Alarms for error rates
   - Log aggregation

2. **Prometheus + Grafana**
   - Metrics collection
   - Dashboards and alerting
   - Historical data visualization

3. **External Monitoring Services**
   - Pingdom
   - UptimeRobot
   - StatusCake

### Health Check Endpoints

The API exposes several health check endpoints:

- `GET /api/v1/health/live` - Liveness probe (Kubernetes)
- `GET /api/v1/health/ready` - Readiness probe (Kubernetes)
- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/detailed` - Comprehensive system health

### Log Files

Application logs are stored in the `logs/` directory:

- `tengen.log` - Main application logs
- `tengen_access.log` - HTTP access logs
- `tengen_errors.log` - Error logs only

Log rotation is configured to keep 5 backup files of 10MB each.

## Alerting

### Recommended Alerts

1. **High Error Rate**
   - Alert when error rate > 5%
   - Check every 5 minutes

2. **High Response Time**
   - Alert when p95 response time > 2 seconds
   - Check every 5 minutes

3. **Service Down**
   - Alert when health checks fail
   - Check every 1 minute

4. **High CPU/Memory Usage**
   - Alert when CPU > 80% or Memory > 85%
   - Check every 5 minutes

### Notification Channels

Configure alerts to notify via:
- Email
- Slack
- PagerDuty
- SMS (for critical alerts)

## Monitoring Best Practices

1. **Set Up Baselines**
   - Run performance tests regularly
   - Establish normal response time ranges
   - Monitor trends over time

2. **Use Multiple Monitoring Layers**
   - Application-level monitoring
   - Infrastructure monitoring
   - External uptime monitoring

3. **Implement Alert Fatigue Prevention**
   - Use appropriate alert thresholds
   - Implement alert escalation policies
   - Regular alert review and tuning

4. **Regular Health Checks**
   - Automated daily health reports
   - Weekly performance reviews
   - Monthly capacity planning reviews
