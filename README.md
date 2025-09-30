# Tengen.ai 🔬

**Tengen.ai** is an intelligent **AI Research Assistant** that automates web research, generates code, and provides comprehensive analysis on any topic. Built with a modern full-stack architecture featuring:

- **FastAPI Backend** with AI-powered research and code generation
- **Next.js Frontend** with TypeScript and modern UI components  
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

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000  
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
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
├── backend/                    # FastAPI Backend
│   ├── api.py                 # Main API endpoints
│   ├── app.py                 # Server startup
│   ├── code_assist.py         # Code generation logic
│   ├── rag_pipeline.py        # RAG implementation
│   ├── web_scraper.py         # Web scraping engine
│   ├── data/                  # Research documents
│   └── db/                    # Vector database
│
├── frontend/                   # Next.js Frontend
│   ├── app/                   # Next.js app directory
│   ├── components/            # React components
│   ├── lib/                   # Utilities and API client
│   └── package.json           # Dependencies
│
├── start_tengen.py            # Complete startup script
├── start_backend.py           # Backend-only startup
├── start_frontend.js          # Frontend-only startup
└── requirements.txt           # Python dependencies
```

---

## 🔧 API Endpoints

### Research & Chat
- `POST /chat` - Main chat interface
- `POST /research` - Research any topic
- `GET /health` - System health check

### Code Assistance
- `POST /code-assist` - Streaming code assistance
- `POST /code/generate` - Generate code snippets
- `POST /code/debug` - Debug code issues

### File Management
- `POST /files/upload` - Upload research documents

---

## 🚀 Deployment

### Local Development
```bash
python start_tengen.py
```

### Production Deployment
1. **Backend**: Deploy FastAPI app to Heroku, Railway, or similar
2. **Frontend**: Deploy Next.js app to Vercel, Netlify, or similar
3. **Environment**: Set production API URLs and keys
- Host frontend on **Vercel**, **Netlify**, or any static hosting service.

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