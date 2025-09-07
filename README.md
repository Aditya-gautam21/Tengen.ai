# Tengen.ai

**Tengen.ai** is an intelligent **Research Assistant** that automates the discovery of relevant online sources and assists with writing or debugging code related to your topic. Built with a modern full-stack setup, it offers fast, dynamic, and interactive functionality through:

- **Python** for backend scraping and logic
- **React + TypeScript** for the frontend interface
- **CSS** for styling and layout orchestration

---

## 🚀 Features

- **Web Research Automation**  
  - Scrapes topically relevant sources across the web and presents them concisely.

- **Code Generation & Debugging**  
  - Automatically generates code snippets or helps debug existing code related to your queried topic.

- **Full‑Stack Architecture**  
  - **Backend**: Python (e.g., FastAPI) handling scraping and AI logic  
  - **Frontend**: React with TypeScript, styled using CSS for a smooth user experience

- **Interactive & Modular**  
  - Component-based structure for scalability and maintainability.

---

## 📦 Requirements

- **Node.js** (16+)  
- **Python** (3.9+)  
- `pip` for backend dependencies

---

## ⚙️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Aditya-gautam21/Tengen.ai.git
cd Tengen.ai
```

### 2. Setup Backend (Python)
```bash
cd backend
pip install -r requirements.txt
# Example command if using FastAPI:
uvicorn main:app --reload
```

### 3. Setup Frontend (React + TypeScript)
```bash
cd frontend
npm install
npm start
```

---

## ▶️ Usage Instructions

1. Launch the **backend server** to enable scraping and code logic.  
2. Start the **frontend React app** in development mode.  
3. Input a topic into the interface:  
   - The assistant fetches relevant online sources.  
   - It then generates or debugs code snippets based on your need.

---

## 📂 Project Structure

```
Tengen.ai/
├── backend/                # Python services
│   ├── main.py             # Backend entrypoint
│   ├── scraper/            # Web scraping logic
│   ├── code_assist/        # Code generation/debugging logic
│   └── requirements.txt    # Python dependencies
│
├── frontend/               # React + TypeScript UI
│   ├── src/
│   │   ├── components/     # Modular UI components
│   │   ├── pages/          # Main screens/pages
│   │   └── styles/         # CSS styling
│   └── package.json        # Frontend dependencies
│
└── README.md               # Project README
```

---

## 🌐 Configuration & Deployment

- Configure scraping logic and source filters in `scraper/config.py` (or similar).  
- Deploy backend on platforms like **Heroku**, **Render**, or **Docker**.  
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
