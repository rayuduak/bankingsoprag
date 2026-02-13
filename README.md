

🏦 Citi-Themed RAG Chat Application (Local LLM with Ollama)

A full-stack ChatGPT-style application that performs Retrieval-Augmented Generation (RAG) on:
	•	📄 Uploaded documents
	•	🌐 Documents ingested from URLs

The system runs fully locally using Ollama with the gemma3:latest model and provides persistent chat memory using Redis.

⸻

🚀 Project Overview

This project implements a ChatGPT-style interface with:
	•	🔹 Local LLM inference via Ollama
	•	🔹 FastAPI backend with Uvicorn
	•	🔹 Vector search using ChromaDB
	•	🔹 Embeddings via open-source embedding models
	•	🔹 Redis-based chat memory & prompt history
	•	🔹 CitiBank-themed frontend UI

The goal is to create a secure, fully local RAG pipeline suitable for enterprise-style deployments.

⸻

🏗️ Architecture

🔹 Backend
	•	Framework: FastAPI
	•	Server: Uvicorn
	•	LLM: Ollama (gemma3:latest)
	•	Vector Database: ChromaDB
	•	Embeddings: Open-source embedding model
	•	Memory & History Storage: Redis

🔹 Frontend
	•	HTML
	•	CSS
	•	JavaScript
	•	Bootstrap
	•	Vite
	•	CitiBank branding theme and logo

⸻

🔍 Core Features

1️⃣ Retrieval-Augmented Generation (RAG)
	•	Upload PDF / text documents
	•	Ingest documents from URLs
	•	Chunking + embedding
	•	Store vectors in ChromaDB
	•	Retrieve relevant context during query

2️⃣ Local LLM Inference
	•	Powered by Ollama
	•	Uses gemma3:latest
	•	Fully offline model execution

3️⃣ Persistent Chat Memory
	•	Chat conversations stored in Redis
	•	Maintains session-based context
	•	Enables multi-turn conversations

4️⃣ Prompt History
	•	All prompts stored in Redis
	•	Displayed in left-side navigation panel
	•	Click to reload previous conversations

5️⃣ Document Management UI
	•	Uploaded documents displayed in UI
	•	URL-ingested documents listed
	•	Allows users to track active knowledge base

⸻

🧠 RAG Pipeline Flow
	1.	Upload document or provide URL
	2.	Extract & clean content
	3.	Chunk text
	4.	Generate embeddings
	5.	Store vectors in ChromaDB
	6.	User sends query
	7.	Retrieve relevant chunks
	8.	Send context + query to LLM
	9.	Generate final response

⸻

🗂️ Project Structure (Example)

/backend
    main.py
    rag_pipeline.py
    redis_memory.py
    chroma_store.py

/frontend
    index.html
    src/
    assets/
    vite.config.js


⸻

⚙️ Requirements

Backend
	•	Python 3.10+
	•	FastAPI
	•	Uvicorn
	•	Redis
	•	ChromaDB
	•	Ollama
	•	Open-source embedding model

Frontend
	•	Node.js
	•	Vite
	•	Bootstrap

⸻

🛠️ Running the Project

1️⃣ Start Ollama

ollama run gemma3:latest

2️⃣ Start Redis

redis-server

3️⃣ Run Backend

uvicorn main:app --reload

4️⃣ Run Frontend

npm install
npm run dev


⸻

🔐 Design Goals
	•	Fully local LLM execution
	•	Enterprise-style UI (Citi theme)
	•	Modular backend design
	•	Scalable vector storage
	•	Persistent memory architecture
	•	Clean separation of frontend and backend

⸻

📌 Future Enhancements
	•	Multi-user authentication
	•	Role-based access control
	•	Document tagging
	•	Streaming responses
	•	Model selection dropdown
	•	Vector DB filtering
	•	Dockerized deployment

⸻

📄 License

MIT License (or specify your license)

⸻

If you want, I can also:
	•	Convert this into a clean GitHub-ready markdown with badges
	•	Create a professional enterprise-style README
	•	Add architecture diagrams (Mermaid)
	•	Generate a Docker Compose setup section
	•	Create a deployment guide for production
