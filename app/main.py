from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from .llm import call_ollama_generate, get_embeddings
from .ingest import ingest_pdf_from_url, ingest_pdf_file
from .vectorstore import ChromaClientWrapper

app = FastAPI(title="Usecase RAG API")

DB_DIR = Path("./chroma_db")
db = ChromaClientWrapper(persist_directory=str(DB_DIR))

# Allow local frontend during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from .history import ChatHistoryManager

history_manager = ChatHistoryManager()

class QueryRequest(BaseModel):
    query: str
    top_k: int = 4
    session_id: str = "default_session"


@app.get("/api/status")
def status():
    return {
        "status": "ok", 
        "model_endpoint": "http://localhost:11434", 
        "chroma_persist": str(DB_DIR),
        "redis_connected": history_manager.enabled
    }


@app.post("/api/query")
async def query(req: QueryRequest):
    if not req.query:
        raise HTTPException(status_code=400, detail="query is required")

    print(f"--- New Query: {req.query} ---")
    
    # Get history for context
    history = history_manager.get_history(req.session_id)
    history_context = ""
    for msg in history:
        history_context += f"{msg['role'].capitalize()}: {msg['content']}\n"

    # compute embedding
    q_emb = get_embeddings([req.query])[0]
    docs = db.similarity_search_by_embedding(q_emb, top_k=req.top_k)
    
    print(f"Retrieved {len(docs)} chunks from vector store.")
    if docs:
        print(f"Top chunk score: {docs[0].get('score')} | Content snippet: {docs[0]['text'][:100]}...")
    else:
        print("WARNING: No relevant chunks retrieved!")

    context_texts = [d["text"] for d in docs]
    prompt = f"""
You are a helpful knowledge assistant. Answer the user's question ONLY using the provided Context and Conversation History below.
If the context does not contain the answer, politely state that you don't have enough information based on the documents.
Always cite the context index [1], [2], etc., when you use information from it.

Conversation History:
{history_context}

Context Information:
"""
    for i, t in enumerate(context_texts, start=1):
        prompt += f"\n[Context {i}]\n{t}\n"
    
    prompt += f"\nUser question: {req.query}\n\nHelpful Answer:"

    # Use streaming
    from fastapi.responses import StreamingResponse
    import json

    async def stream_generator():
        # First yield the sources as a JSON line
        yield json.dumps({"type": "sources", "data": docs}) + "\n"
        
        full_answer = ""
        try:
            gen = call_ollama_generate(prompt, model="gemma3:latest", stream=True)
            for chunk in gen:
                if chunk:
                    full_answer += chunk
                    yield json.dumps({"type": "chunk", "data": chunk}) + "\n"
        except Exception as e:
            print(f"Streaming error: {e}")
            yield json.dumps({"type": "chunk", "data": f"\n[Error: {str(e)}]"}) + "\n"
            
        # Finally save to history
        if full_answer:
            history_manager.save_message(req.session_id, "user", req.query)
            history_manager.save_message(req.session_id, "assistant", full_answer)
        
        yield json.dumps({"type": "done"}) + "\n"

    return StreamingResponse(stream_generator(), media_type="application/x-ndjson")


@app.post("/api/ingest")
def ingest(payload: dict):
    # Accept JSON {"url": "https://..."} to fetch a PDF and ingest it.
    url = payload.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="url is required in JSON body")

    try:
        count = ingest_pdf_from_url(url, persist_directory=str(DB_DIR))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ingest failed: {e}")
    return {"status": "ok", "ingested_chunks": count}


@app.post("/api/reset")
def reset_db():
    try:
        db.reset_collections()
        # Also clear redis history if needed, but the user mostly meant chroma
        return {"status": "ok", "message": "Database cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reset failed: {e}")


@app.post("/api/ingest/upload")
async def ingest_upload(file: UploadFile = File(...)):
    # Accept uploaded PDF file
    if not file.filename:
        raise HTTPException(status_code=400, detail="file required")

    from datetime import datetime
    import os
    
    # Create uploaded_files dir if not exists
    UPLOAD_DIR = Path("uploaded_files")
    UPLOAD_DIR.mkdir(exist_ok=True)
    
    # Save file to persistent storage
    file_path = UPLOAD_DIR / file.filename
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    file_size = len(content)
    timestamp = datetime.now().isoformat()

    try:
        # 1. Save file-level metadata to Chroma
        db.save_file_metadata(file.filename, file_size, timestamp)
        
        # 2. Ingest the file (chunking, embedding, upserting chunks)
        count = ingest_pdf_file(file_path, persist_directory=str(DB_DIR), source_name=file.filename)
        
        return {
            "status": "ok", 
            "ingested_chunks": count, 
            "file_info": {
                "name": file.filename,
                "size": file_size,
                "timestamp": timestamp
            }
        }
    except Exception as e:
        # cleanup file if ingestion failed? Maybe keep it for debug.
        raise HTTPException(status_code=500, detail=f"Upload processing failed: {e}")


@app.get("/api/docs")
def list_docs():
    items = db.list_documents()
    return {"docs": items}
