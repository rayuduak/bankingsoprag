# Setup and Execution Guide

This document provides instructions on how to set up, run, and maintain the AI-Powered Knowledge Chatbot.

## 1. Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **Ollama**: Installed and running locally.
  - Pull the required model: `ollama pull gemma3:latest`
- **Redis**: Installed and running locally (port 6379) for chat history.

## 2. Installation

### Backend Setup
1. Create a virtual environment:
   ```powershell
   python -m venv .venv
   ```
2. Activate the virtual environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```powershell
   cd frontend
   ```
2. Install npm packages:
   ```powershell
   npm install
   ```

## 3. Running the Application

### Start the Backend
From the root directory:
```powershell
.\.venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*The backend will be available at http://localhost:8000*

### Start the Frontend
From the `frontend` directory:
```powershell
npm run dev
```
*The frontend will be available at http://localhost:5173*

## 4. Usage Instructions

1. **Upload Documents**: Use the "Upload Local PDF" button to ingest documents. Chunks will be created using `sentence-transformers` and stored in `chroma_db`.
2. **Ask Questions**: Type your query in the input box. The system will retrieve relevant context from your documents and stream the answer from Ollama.
3. **Chat History**: The system uses Redis to remember context within a session.

## 5. Maintenance and Troubleshooting

### Cleanup (Start Fresh)
To clear all ingested documents and metadata:
- Click the **"Clear Database"** button in the UI.
- OR manually delete the `chroma_db` folder:
  ```powershell
  Remove-Item -Path "chroma_db" -Recurse -Force
  ```

### Running Tests
To verify the backend functionality:
```powershell
.\.venv\Scripts\python run_tests.py
```

### Manual Ingestion Script
You can also ingest files via the command line:
```powershell
.\.venv\Scripts\python scripts/ingest.py --pdf "path/to/your/file.pdf"
```

## 6. Environment Variables (`.env`)
Ensure your `.env` file in the root directory contains:
```ini
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:latest
REDIS_HOST=localhost
REDIS_PORT=6379
```
