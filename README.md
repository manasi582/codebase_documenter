# Autonomous Codebase Documenter

<div align="center">

![Codebase Documenter](https://img.shields.io/badge/AI-Powered-purple?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.11+-green?style=for-the-badge)
![Next.js](https://img.shields.io/badge/next.js-14-black?style=for-the-badge)

**Transform any GitHub repository into comprehensive, AI-generated documentation in minutes**

[Features](#features) • [Quick Start](#quick-start) • [Architecture](#architecture) • [Usage](#usage)

</div>

---

##  Features

- **AI-Powered Analysis**: Uses GPT-4 and LangGraph to deeply understand your codebase
- **Complete Documentation**: Generates main README, folder READMEs, function docs, and setup guides
- **Lightning Fast**: Asynchronous processing with Celery for handling multiple repositories
- **💾 Local Storage**: Documentation saved locally for easy access
- **Beautiful UI**: Modern, responsive Next.js frontend with glassmorphism and animations
- **Real-time Updates**: Live progress tracking during documentation generation

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Next.js   │─────▶│   FastAPI    │─────▶│   Celery    │
│  Frontend   │      │   Backend    │      │   Worker    │
└─────────────┘      └──────────────┘      └─────────────┘
                            │                      │
                            ▼                      ▼
                     ┌──────────────┐      ┌─────────────┐
                     │    Redis     │      │  LangGraph  │
                     │  Task Queue  │      │  AI Agent   │
                     └──────────────┘      └─────────────┘
                                                  │
                                                  ▼
                                           ┌─────────────┐
                                           │   Local     │
                                           │   Storage   │
                                           └─────────────┘
```

### Technology Stack

**Backend:**
- FastAPI - Modern Python web framework
- Celery - Distributed task queue
- Redis - Message broker
- LangGraph - AI agent orchestration
- OpenAI GPT-4 - Code analysis and documentation generation

**Frontend:**
- Next.js 14 - React framework
- Tailwind CSS - Styling
- Framer Motion - Animations
- TypeScript - Type safety

**Infrastructure:**
- Docker & Docker Compose - Containerization
- Local File System - Documentation storage
- GitPython - Repository cloning

##  Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API key
- Git



### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd codebase_documenter
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your OpenAI API key:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   ```
   
   **Note:** Documentation will be saved to `/tmp/codebase_docs` on your local system.

3. **Start the application**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 📖 Usage

### Web Interface

1. Open http://localhost:3000 in your browser
2. Enter a GitHub repository URL (e.g., `https://github.com/username/repo`)
3. Click "Generate Documentation"
4. Monitor the progress in real-time
5. Download the generated documentation when complete

### API Usage

**Submit a repository for analysis:**
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"github_url": "https://github.com/username/repo"}'
```

**Check job status:**
```bash
curl http://localhost:8000/api/status/{job_id}
```

**Get results:**
```bash
curl http://localhost:8000/api/result/{job_id}
```

## 📁 Project Structure

```
codebase_documenter/
├── backend/              # FastAPI application
│   ├── app.py           # Main API endpoints
│   ├── celery_app.py    # Celery configuration
│   ├── tasks.py         # Async tasks
│   └── config.py        # Settings
├── ai_agent/            # AI documentation agent
│   ├── agent.py         # LangGraph workflow
│   ├── prompts.py       # LLM prompts
│   └── utils.py         # Helper functions
├── services/            # Service layer
│   ├── git_service.py   # Git operations
│   ├── local_storage.py # Local storage operations
│   └── file_analyzer.py # File analysis
├── frontend/            # Next.js application
│   └── src/
│       ├── app/         # Pages
│       └── components/  # React components
└── docker-compose.yml   # Docker orchestration
```

## 🔧 Development

### Running Locally (without Docker)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload
```

**Celery Worker:**
```bash
celery -A celery_app worker --loglevel=info
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Redis:**
```bash
redis-server
```

##  Testing

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm test
```

##  Generated Documentation

The AI agent generates:

1. **Main README.md** - Comprehensive project overview
2. **Folder READMEs** - Documentation for each major directory
3. **Function Documentation** - Detailed explanations of key files
4. **SETUP.md** - Complete installation and setup guide

##  Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

##  Acknowledgments

- OpenAI for GPT-4 API
- LangChain and LangGraph teams
- FastAPI and Next.js communities

---


