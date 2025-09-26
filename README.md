# Law-GPT

A comprehensive legal research and document analysis platform powered by AI, designed specifically for Indian legal professionals and researchers.

🚀 **Now with full Indian Kanoon API integration and production-ready Docker deployment!**

## ⚡ Quick Production Deployment

Deploy Law-GPT as a production website in minutes:

```bash
# 1. Clone the repository
git clone <repository-url>
cd Law-GPT

# 2. Configure API keys
cp .env.example .env
# Edit .env with your Indian Kanoon API key and other credentials

# 3. Deploy with one command
./deploy.sh  # Linux/macOS
# OR
.\deploy.ps1  # Windows

# 4. Access your application
# Main app: http://localhost
# API: http://localhost:8000
```

For detailed deployment instructions, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

## Local Development Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+ with pgvector extension (optional, SQLite can be used for local development)
- OpenAI API key

### Backend Setup

1. Create a virtual environment and activate it:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
cd backend
pip install -r requirements.txt
```

3. Database Setup:

   **Option 1: PostgreSQL (recommended for production)**
   ```powershell
   .\scripts\init_db.ps1
   ```

   **Option 2: SQLite (simpler for local development)**
   ```powershell
   .\scripts\setup_sqlite.ps1
   ```

4. Update the `.env` file in the `backend` directory with your OpenAI API key and other settings.

### Frontend Setup

1. Install dependencies:

```powershell
cd frontend
npm install
```

### Running the Application

You can run both the backend and frontend using the provided script:

```powershell
.\scripts\run_local.ps1
```

Or run them separately:

- Backend: `cd backend && uvicorn app.main:app --reload --port 8000`
- Frontend: `cd frontend && npm run dev`

## Features

- User authentication
- Document upload and analysis
- Legal question answering with citations
- Document management

## Project Structure

- `backend/`: FastAPI backend application
- `frontend/`: React frontend application
- `scripts/`: Utility scripts for development
- `sample_data/`: Sample legal documents for testing
