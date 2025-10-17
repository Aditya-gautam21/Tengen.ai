# Tengen.ai 🔬

**Tengen.ai** is a production-ready **AI Research Assistant** that automates web research, generates code, and provides comprehensive analysis on any topic. Built with enterprise-grade architecture featuring:

- **FastAPI Backend** with RESTful APIs and microservices architecture
- **Containerized Deployment** with Docker and Kubernetes support
- **CI/CD Pipeline** with GitHub Actions for automated deployment
- **Cloud-Native** design for AWS, GCP, and Azure deployment
- **Monitoring & Observability** with comprehensive logging and health checks
- **RAG Pipeline** for intelligent document processing and retrieval
- **Web Scraping** capabilities for real-time research

---

## 🚀 Features

### 🔍 **Intelligent Web Research**
- Automated web scraping for any research topic
- AI-powered content analysis and summarization
- Source verification and relevance scoring

### 💻 **Code Generation & Debugging**
- Generate code snippets in multiple languages
- Debug and optimize existing code
- Best practices recommendations

### 🧠 **RAG-Powered Knowledge Base**
- Upload and process research documents
- Intelligent question-answering system
- Context-aware responses using vector embeddings

### 🎨 **Modern UI/UX**
- Clean, responsive interface
- Real-time streaming responses
- Interactive research panels

---

## 📦 System Requirements

- **Python 3.9+** with pip
- **Node.js 18+** with npm
- **Google Gemini API Key** (for AI functionality)

---

## 🚀 Quick Start

### Option 1: First-Time Setup (Run Once)
```bash
git clone https://github.com/Aditya-gautam21/Tengen.ai.git
cd Tengen.ai
python setup_first_time.py  # Install everything once
# Edit backend/.env with your Google API key
python start_tengen.py      # Fast startup from now on
```

### Option 2: Quick Start (After First Setup)
```bash
# After running setup_first_time.py once:
python start_tengen.py  # Fast startup, no dependency installation
```

### Option 3: Manual Setup
```bash
# 1. Install dependencies
python install_dependencies.py

# 2. Configure API key
echo "GOOGLE_API_KEY=your_actual_api_key_here" > backend/.env

# 3. Start application
python start_tengen.py
```

---

## 🔑 API Key Setup

1. Get your Google Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Edit `backend/.env`:
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

---

## 🌐 Access Points

Once running, access the application at:

### Local Development
- **Backend API**: http://localhost:8080  
- **API Documentation**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/api/v1/health
- **Frontend UI**: http://localhost:3000 (if running frontend)

### Production Endpoints
- **API Base**: https://your-api-domain.com/api/v1
- **Interactive Docs**: https://your-api-domain.com/docs
- **Health Monitoring**: https://your-api-domain.com/api/v1/health/detailed
- **Streamlit App**: https://tengen-ai.streamlit.app (if using Streamlit Cloud)
---

## 📖 Usage Guide

### 🔍 Research Topics
1. Enter any research topic in the search field
2. Click "Research" to start web scraping
3. View summarized results with source links
4. Ask follow-up questions about the research

### 💻 Code Assistance  
1. Use the `/code-assist` endpoint for code generation
2. Use the `/code/debug` endpoint for debugging
3. Specify programming language for better results

### 📄 Document Upload
1. Upload JSON research files via `/files/upload`
2. Documents are automatically processed for Q&A
3. Query your uploaded documents through the chat interface

---

## 🏗️ Architecture

```
Tengen.ai/
├── backend/                    # Production FastAPI Backend
│   ├── main.py                # Production application entry point
│   ├── services/              # Modular service layer
│   │   ├── inference.py       # AI inference service
│   │   ├── health.py          # Health monitoring service
│   │   └── base_service.py    # Base service class
│   ├── api/                   # API routes
│   │   └── routes/            # Organized route handlers
│   ├── utils/                 # Utilities and middleware
│   │   ├── logger.py          # Production logging
│   │   └── middleware.py      # Security & monitoring middleware
│   ├── code_assist.py         # Code generation logic
│   ├── rag_pipeline.py        # RAG implementation
│   ├── data/                  # Research documents
│   └── db/                    # Vector database
│
├── frontend/                   # Next.js Frontend
│   ├── app/                   # Next.js app directory
│   ├── components/            # React components
│   ├── lib/                   # Utilities and API client
│   └── package.json           # Dependencies
│
├── aws/                       # AWS deployment configurations
│   ├── cloudformation-template.yaml  # Infrastructure as Code
│   ├── ecs-task-definition.json      # ECS task configuration
│   └── ecs-service.json              # ECS service configuration
│
├── monitoring/                # Monitoring and observability
│   ├── uptime_monitor.py      # Uptime monitoring script
│   └── performance_monitor.py # Performance testing tool
│
├── docs/                      # Documentation
│   └── deployment.md          # Comprehensive deployment guide
│
├── .github/workflows/         # CI/CD pipeline
│   └── deploy.yml             # GitHub Actions workflow
│
├── Dockerfile                 # Production container image
├── docker-compose.yml         # Local development orchestration
├── streamlit_app.py           # Streamlit Cloud deployment
└── requirements.txt           # Python dependencies
```

---

## 🔧 API Endpoints

### AI Inference & Predictions
- `POST /api/v1/predict` - Main prediction endpoint
- `POST /api/v1/predict/batch` - Batch prediction processing
- `GET /api/v1/model/info` - Model information and capabilities

### Code Generation & Debugging
- `POST /api/v1/code/generate` - Generate code snippets
- `POST /api/v1/code/debug` - Debug and analyze code
- `POST /api/v1/research` - Research topics and documents

### Health & Monitoring
- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/detailed` - Comprehensive system health
- `GET /api/v1/health/live` - Liveness probe (Kubernetes)
- `GET /api/v1/health/ready` - Readiness probe (Kubernetes)

### Logging & Administration
- `GET /api/v1/logs` - Retrieve application logs
- `GET /api/v1/logs/download` - Download log files
- `DELETE /api/v1/logs` - Clear log files

### Legacy Endpoints (for backward compatibility)
- `POST /chat` - Main chat interface
- `POST /code-assist` - Streaming code assistance
- `POST /files/upload` - Upload research documents

---

## 🚀 Deployment

### Quick Start with Docker

```bash
# Clone and setup
git clone https://github.com/your-org/tengen.ai.git
cd tengen.ai

# Set environment variables
echo "GOOGLE_API_KEY=your_actual_api_key_here" > .env

# Run with Docker Compose
docker-compose up --build
```

### Production Deployment Options

#### 1. AWS ECS with Fargate (Recommended)
```bash
# Deploy with CloudFormation
aws cloudformation create-stack \
  --stack-name tengen-production \
  --template-body file://aws/cloudformation-template.yaml \
  --parameters ParameterKey=GoogleAPIKey,ParameterValue=your_api_key \
  --capabilities CAPABILITY_IAM
```

#### 2. Streamlit Cloud (Simple)
- Connect GitHub repository to Streamlit Cloud
- Set environment variables in dashboard
- Deploy automatically on git push

#### 3. Kubernetes
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/
```

#### 4. Traditional VPS/Cloud
```bash
# Install Docker and run
docker run -d -p 8080:8080 \
  -e GOOGLE_API_KEY=your_api_key \
  tengen-ai:latest
```

### CI/CD Pipeline

The project includes automated CI/CD with GitHub Actions:
- ✅ Automated testing and security scanning
- ✅ Docker image building and pushing
- ✅ AWS ECS deployment
- ✅ Streamlit Cloud deployment
- ✅ Slack notifications

**Setup**: Configure secrets in GitHub repository settings.

---

## 📊 Monitoring & Observability

### Health Monitoring
- **Uptime Monitoring**: Automated health checks every 60 seconds
- **Performance Testing**: Comprehensive response time and throughput metrics
- **System Resources**: CPU, memory, and disk usage monitoring
- **Error Tracking**: Centralized error logging and alerting

### Logging
- **Structured Logging**: JSON-formatted logs with rotation
- **Multiple Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log Aggregation**: Centralized log collection and analysis
- **Real-time Monitoring**: Live log streaming and analysis

### Monitoring Tools
```bash
# Run uptime monitoring
python monitoring/uptime_monitor.py --api-url https://your-api.com

# Run performance tests
python monitoring/performance_monitor.py --iterations 20

# Check system health
curl https://your-api.com/api/v1/health/detailed
```

---

## 🔒 Production Features

### Security
- **Non-root Container**: Runs as non-privileged user
- **Security Headers**: CSRF, XSS, and clickjacking protection
- **Rate Limiting**: Configurable request rate limits
- **Input Validation**: Comprehensive request validation
- **Secrets Management**: Secure environment variable handling

### Scalability
- **Horizontal Scaling**: Multiple container instances
- **Load Balancing**: Automatic request distribution
- **Auto Scaling**: CPU and memory-based scaling policies
- **Stateless Design**: No session dependencies

### Reliability
- **Health Checks**: Kubernetes-ready liveness and readiness probes
- **Graceful Shutdown**: Proper application lifecycle management
- **Error Handling**: Comprehensive error recovery and reporting
- **Circuit Breakers**: Fault tolerance patterns

---

## 🤝 Contributing

1. Fork the repository  
2. Create a feature branch:
   ```bash
   git checkout -b feature/my-new-feature
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add awesome new feature"
   ```
4. Push and open a Pull Request  

---

## 📜 License

This project is open-source under the **MIT License**.

---

## 🙏 Acknowledgements

- **FastAPI** (or preferred Python framework) – Backend framework  
- **React + TypeScript** – Frontend UI  
- **BeautifulSoup / Scrapy** – Web scraping tools  
- **Axios or Fetch API** – Client-side API calls  

---

## ⭐ About

Tengen.ai is a full‑stack research assistant that combines **web scraping** and **AI-powered code assistance** to support developers, researchers, and learners with both quick information retrieval and code-based solutions—all wrapped up in a modern React + Python interface.

---

## 🔧 Troubleshooting

### Installation Issues

If dependencies fail to install:

1. **Use robust installer**: `python install_dependencies.py`
2. **Try minimal install**: `pip install -r requirements-minimal.txt`  
3. **Check Python version**: Must be 3.9+
4. **Check Node.js version**: Must be 18+

### Common Fixes

- **API Key Error**: Edit `backend/.env` with your Google Gemini API key
- **Port 8000 in use**: Kill existing process or change port in `backend/app.py`
- **Module not found**: Run `pip install -r requirements.txt`
- **npm install fails**: Run `cd frontend && npm cache clean --force && npm install`

### Detailed Help

For comprehensive troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### Quick Test

```bash
# Test your setup
python test_setup.py

# Test API (after starting backend)
python test_api.py
```

---

## 📞 Support

- 📖 **Setup Guide**: [SETUP_GUIDE.md](SETUP_GUIDE.md)
- 🔧 **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- 🧪 **Testing**: `python test_setup.py`
- 🚀 **Quick Install**: `python install_dependencies.py`