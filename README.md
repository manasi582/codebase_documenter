# Autonomous Codebase Documenter

<div align="center">

**Automate Documentation. Accelerate Development.**

[Features](#features) • [Quick Start](#quick-start) • [Architecture](#architecture) • [Usage](#usage)

</div>

---

##  Features

- **AI-Powered Analysis**: Uses GPT-4 and LangGraph to deeply understand your codebase
- **Complete Documentation**: Generates main README, folder READMEs, function docs, and setup guides
- **Lightning Fast**: Asynchronous processing with Celery for handling multiple repositories
- **Local Storage**: Documentation saved locally for easy access
- **UI**: Modern, responsive Next.js frontend with glassmorphism and animations
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
- Local File System - Documentation storage
- GitPython - Repository cloning

##  Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Redis
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

3. **Install Redis**
   ```bash
   # macOS
   brew install redis
   brew services start redis
   
   # Or run manually
   redis-server
   ```

4. **Set up Backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

5. **Set up Frontend**
   ```bash
   cd frontend
   npm install
   ```

6. **Start the application**
   
   Open 3 terminal windows:
   
   **Terminal 1 - Backend:**
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```
   
   **Terminal 2 - Celery Worker:**
   ```bash
   cd backend
   source venv/bin/activate
   celery -A celery_app worker --loglevel=info
   ```
   
   **Terminal 3 - Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

7. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Usage

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

##  Project Structure

```
codebase_documenter/
├── backend/              # FastAPI application
│   ├── app.py           # Main API endpoints
│   ├── celery_app.py    # Celery configuration
│   ├── tasks.py         # Async tasks
│   ├── config.py        # Settings
│   └── requirements.txt # Python dependencies
├── ai_agent/            # AI documentation agent
│   ├── agent.py         # LangGraph workflow
│   ├── prompts.py       # LLM prompts
│   └── utils.py         # Helper functions
├── services/            # Service layer
│   ├── git_service.py   # Git operations
│   ├── local_storage.py # Local storage operations
│   └── file_analyzer.py # File analysis
├── frontend/            # Next.js application
│   ├── package.json     # Node dependencies
│   └── src/
│       ├── app/         # Pages
│       └── components/  # React components
├── .env.example         # Environment template
└── README.md            # Documentation
```

## Development

### Environment Variables

Make sure your `.env` file is properly configured with your API keys:
```env
OPENAI_API_KEY=your_actual_key_here
# or
GROQ_API_KEY=your_actual_key_here
```

### Troubleshooting

**Redis Connection Issues:**
```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG
```

**Port Already in Use:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```


## Testing

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


