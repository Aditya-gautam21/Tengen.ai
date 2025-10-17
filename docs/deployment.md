# Tengen.ai Deployment Guide

This guide covers deploying Tengen.ai to production environments with containerization, CI/CD, and monitoring.

## Table of Contents

- [Quick Start](#quick-start)
- [Environment Setup](#environment-setup)
- [Docker Deployment](#docker-deployment)
- [AWS Deployment](#aws-deployment)
- [Streamlit Cloud Deployment](#streamlit-cloud-deployment)
- [CI/CD Pipeline](#cicd-pipeline)
- [Monitoring & Observability](#monitoring--observability)
- [Troubleshooting](#troubleshooting)

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Google Gemini API Key
- Git

### Local Development with Docker

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/tengen.ai.git
   cd tengen.ai
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your Google API key
   echo "GOOGLE_API_KEY=your_actual_api_key_here" >> .env
   ```

3. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - API: http://localhost:8080
   - API Docs: http://localhost:8080/docs
   - Health Check: http://localhost:8080/api/v1/health

## Environment Setup

### Required Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GOOGLE_API_KEY` | Google Gemini API key | Yes | - |
| `HOST` | Server host | No | `0.0.0.0` |
| `PORT` | Server port | No | `8080` |
| `LOG_LEVEL` | Logging level | No | `INFO` |
| `ENVIRONMENT` | Deployment environment | No | `development` |

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MAX_WORKERS` | Number of worker processes | `1` |
| `CORS_ORIGINS` | Allowed CORS origins | `*` |
| `TRUSTED_HOSTS` | Trusted host patterns | `*` |

## Docker Deployment

### Production Dockerfile

The production Dockerfile includes:
- Multi-stage build for optimization
- Non-root user for security
- Health checks
- Proper logging configuration

### Build and Run

```bash
# Build the image
docker build -t tengen-ai:latest .

# Run the container
docker run -d \
  --name tengen-api \
  -p 8080:8080 \
  -e GOOGLE_API_KEY=your_api_key \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/data:/app/data \
  tengen-ai:latest
```

### Docker Compose for Production

```yaml
version: '3.8'
services:
  tengen-api:
    build: .
    ports:
      - "8080:8080"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/api/v1/health/live"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## AWS Deployment

### Option 1: AWS ECS with Fargate

1. **Prerequisites**
   - AWS CLI configured
   - Docker Hub account
   - ECR repository (optional)

2. **Deploy with CloudFormation**
   ```bash
   # Update the CloudFormation template with your values
   aws cloudformation create-stack \
     --stack-name tengen-production \
     --template-body file://aws/cloudformation-template.yaml \
     --parameters ParameterKey=GoogleAPIKey,ParameterValue=your_api_key \
     --capabilities CAPABILITY_IAM
   ```

3. **Manual ECS Deployment**
   ```bash
   # Register task definition
   aws ecs register-task-definition --cli-input-json file://aws/ecs-task-definition.json
   
   # Create service
   aws ecs create-service --cli-input-json file://aws/ecs-service.json
   ```

### Option 2: AWS EC2

1. **Launch EC2 instance**
   ```bash
   # Use Amazon Linux 2 AMI
   aws ec2 run-instances \
     --image-id ami-0abcdef1234567890 \
     --instance-type t3.medium \
     --key-name your-key-pair \
     --security-group-ids sg-12345678
   ```

2. **Install Docker and run application**
   ```bash
   # SSH into instance
   ssh -i your-key.pem ec2-user@your-instance-ip
   
   # Install Docker
   sudo yum update -y
   sudo yum install -y docker
   sudo systemctl start docker
   sudo usermod -a -G docker ec2-user
   
   # Clone and run application
   git clone https://github.com/your-org/tengen.ai.git
   cd tengen.ai
   docker-compose up -d
   ```

### Load Balancing and Auto Scaling

The CloudFormation template includes:
- Application Load Balancer
- Auto Scaling Group
- Target tracking scaling policies
- Health checks

## Streamlit Cloud Deployment

### Setup

1. **Prepare Streamlit app**
   - The `streamlit_app.py` file is ready for deployment
   - Configure API endpoint in environment variables

2. **Deploy to Streamlit Cloud**
   ```bash
   # Connect your GitHub repository to Streamlit Cloud
   # Set environment variables in Streamlit Cloud dashboard:
   # - API_BASE_URL: Your deployed API URL
   # - GOOGLE_API_KEY: Your API key
   ```

3. **Access the application**
   - Your app will be available at: `https://tengen-ai.streamlit.app`

## CI/CD Pipeline

### GitHub Actions Setup

1. **Required Secrets**
   Configure these secrets in your GitHub repository:

   ```
   DOCKER_USERNAME=your_dockerhub_username
   DOCKER_PASSWORD=your_dockerhub_password
   GOOGLE_API_KEY=your_google_api_key
   AWS_ACCESS_KEY_ID=your_aws_access_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret_key
   STREAMLIT_TOKEN=your_streamlit_token (optional)
   SLACK_WEBHOOK=your_slack_webhook (optional)
   ```

2. **Pipeline Features**
   - Automated testing
   - Security scanning with Trivy
   - Docker image building and pushing
   - AWS ECS deployment
   - Streamlit Cloud deployment
   - Slack notifications

3. **Manual Deployment**
   ```bash
   # Trigger deployment manually
   git tag v1.0.0
   git push origin v1.0.0
   ```

## Monitoring & Observability

### Health Checks

The API provides multiple health check endpoints:

- `GET /api/v1/health/live` - Liveness probe
- `GET /api/v1/health/ready` - Readiness probe
- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/detailed` - Comprehensive health status

### Logging

- **Application Logs**: `logs/tengen.log`
- **Access Logs**: `logs/tengen_access.log`
- **Error Logs**: `logs/tengen_errors.log`
- **Log Rotation**: 10MB files, 5 backups

### Monitoring Tools

1. **Uptime Monitoring**
   ```bash
   python monitoring/uptime_monitor.py --api-url https://your-api.com
   ```

2. **Performance Testing**
   ```bash
   python monitoring/performance_monitor.py --api-url https://your-api.com
   ```

### External Monitoring

Integrate with external monitoring services:

- **Pingdom**: HTTP monitoring
- **UptimeRobot**: Multi-protocol monitoring
- **StatusCake**: Comprehensive monitoring

## Troubleshooting

### Common Issues

1. **API Key Not Working**
   ```bash
   # Check environment variable
   docker exec -it tengen-api env | grep GOOGLE_API_KEY
   
   # Test API key
   curl -H "Authorization: Bearer $GOOGLE_API_KEY" \
        https://generativelanguage.googleapis.com/v1/models
   ```

2. **Container Won't Start**
   ```bash
   # Check container logs
   docker logs tengen-api
   
   # Check health status
   docker inspect tengen-api | grep Health -A 10
   ```

3. **High Memory Usage**
   ```bash
   # Monitor container resources
   docker stats tengen-api
   
   # Check application logs for memory issues
   tail -f logs/tengen.log | grep -i memory
   ```

4. **Slow Response Times**
   ```bash
   # Run performance test
   python monitoring/performance_monitor.py
   
   # Check system resources
   curl http://localhost:8080/api/v1/health/detailed
   ```

### Debug Mode

Enable debug mode for detailed logging:

```bash
docker run -e LOG_LEVEL=DEBUG tengen-ai:latest
```

### Log Analysis

```bash
# View recent errors
tail -100 logs/tengen_errors.log

# Search for specific patterns
grep -i "error" logs/tengen.log | tail -20

# Monitor real-time logs
tail -f logs/tengen.log
```

## Security Considerations

1. **Environment Variables**
   - Never commit API keys to version control
   - Use AWS Secrets Manager for production
   - Rotate API keys regularly

2. **Network Security**
   - Use HTTPS in production
   - Configure proper CORS policies
   - Implement rate limiting

3. **Container Security**
   - Run containers as non-root user
   - Keep base images updated
   - Scan images for vulnerabilities

4. **Access Control**
   - Implement authentication for admin endpoints
   - Use API keys for external access
   - Monitor access patterns

## Performance Optimization

1. **Caching**
   - Implement Redis for response caching
   - Use CDN for static assets
   - Cache API responses

2. **Scaling**
   - Use horizontal pod autoscaling
   - Implement load balancing
   - Monitor resource utilization

3. **Database Optimization**
   - Use connection pooling
   - Implement query optimization
   - Monitor database performance

## Backup and Recovery

1. **Data Backup**
   ```bash
   # Backup application data
   docker exec tengen-api tar -czf /tmp/backup.tar.gz /app/data /app/db
   docker cp tengen-api:/tmp/backup.tar.gz ./backup-$(date +%Y%m%d).tar.gz
   ```

2. **Configuration Backup**
   ```bash
   # Backup environment configuration
   docker inspect tengen-api > config-backup.json
   ```

3. **Recovery Process**
   ```bash
   # Restore from backup
   docker cp backup-20240101.tar.gz new-container:/tmp/
   docker exec new-container tar -xzf /tmp/backup-20240101.tar.gz -C /
   ```
