# RAG-11 Complete Startup Guide

## 🚀 Quick Start (5 minutes)

### Prerequisites
- Docker & Docker Compose installed
- GROQ API Key from https://console.groq.com/keys
- Terminal/CMD open in `D:\BAI_TAP\code\vinvuong\rag_11`

### Run It Now
```cmd
docker compose up -d
```

Then open: **http://localhost:5000** in your browser ✅

---

## 📋 What You Just Deployed

**RAG-11** is a full-stack Retrieval-Augmented Generation (RAG) system:

- **Frontend**: Web UI at `http://localhost:5000` (HTML/CSS/JS)
- **API**: Flask REST API on port 5000
- **Vector DB**: FAISS in-memory search
- **LLM**: Groq with gpt-oss-120b model
- **Container**: Docker multi-stage build
- **Persistence**: `rag_index/` folder stores documents

---

## 📁 Project Files & What They Do

```
rag_11/
│
├── 🚀 STARTUP & DEPLOYMENT
│   ├── docker-compose.yml      ← Run with: docker compose up -d
│   ├── Dockerfile              ← Container definition (multi-stage)
│   ├── .env                    ← Your GROQ_API_KEY (keep secret!)
│   ├── .env.example            ← Template for team
│   ├── railway.json            ← Production deployment config
│   ├── rag.bat                 ← Windows CMD shortcut script
│   └── rag.sh                  ← Linux/Mac shortcut script
│
├── 📚 DOCUMENTATION
│   ├── QUICKREF.md             ← This page (you are here)
│   ├── DEPLOYMENT.md           ← Full deployment guide
│   ├── RAILWAY.md              ← Deploy to Railway cloud
│   └── README.md               ← Original project docs
│
├── 🐍 BACKEND CODE
│   ├── api_server.py           ← Flask API server (main entry point)
│   ├── main.py                 ← CLI tool for ingestion & querying
│   ├── ingestion.py            ← Document loading & chunking
│   ├── retriever.py            ← FAISS vector search
│   ├── reranker.py             ← Re-rank results by relevance
│   ├── generator.py            ← Groq LLM integration
│   ├── context_builder.py      ← Assemble context for LLM
│   ├── utils.py                ← Helper functions
│   └── requirements.txt        ← Python dependencies
│
├── 🎨 FRONTEND CODE
│   ├── index.html              ← Web UI
│   ├── style.css               ← Styles
│   ├── script.js               ← Frontend logic
│   └── .dockerignore           ← What Docker excludes from build
│
└── 📊 DATA
    ├── rag_index/              ← FAISS index (documents + vectors)
    ├── __pycache__/            ← Python cache (ignore)
    ├── extras/                 ← Extra files
    └── docker/                 ← Docker helper scripts
```

---

## 🎯 How It Works (Architecture)

```
┌─────────────────────────────────────────────────────┐
│                   USER BROWSER                       │
│           http://localhost:5000                      │
├─────────────────────────────────────────────────────┤
│                    FRONTEND (HTML/JS)                │
├─────────────────────────────────────────────────────┤
│                  FLASK API SERVER                    │
│ api_server.py runs on port 5000                     │
├─────────────────────────────────────────────────────┤
│  RAG PIPELINE (All in api_server.py init_rag())    │
│                                                      │
│  1. INGESTION PIPELINE                              │
│     └─ Load & chunk documents                       │
│     └─ Encode to embeddings (all-MiniLM-L6-v2)     │
│     └─ Store in FAISS index                         │
│                                                      │
│  2. RETRIEVER (Hybrid)                              │
│     ├─ Dense: FAISS vector similarity               │
│     └─ Sparse: BM25 keyword search                  │
│                                                      │
│  3. RERANKER                                        │
│     └─ Re-rank top-k by relevance                   │
│     └─ Model: cross-encoder/ms-marco-MiniLM-L-6-v2│
│                                                      │
│  4. CONTEXT BUILDER                                 │
│     └─ Assemble chunks into LLM prompt              │
│                                                      │
│  5. GENERATOR (Groq LLM)                            │
│     └─ Call Groq API with context                   │
│     └─ Model: openai/gpt-oss-120b                   │
│     └─ Returns answer + citations                   │
│                                                      │
├─────────────────────────────────────────────────────┤
│                   PERSISTENCE                        │
│              rag_index/ (FAISS vectors)             │
│              Contains: chunks, embeddings, metadata  │
└─────────────────────────────────────────────────────┘
```

---

## 🔧 Common Tasks

### 1️⃣ Start the App

#### Option A: Docker Compose (Recommended)
```cmd
docker compose up -d
```

#### Option B: Direct Python
```cmd
python api_server.py
```

#### Option C: Docker Manual
```cmd
docker build -t rag-11:latest .
docker run -p 5000:5000 -e GROQ_API_KEY='your-key' --name rag-app rag-11:latest
```

---

### 2️⃣ Add Documents

#### From CLI (Recommended)
```cmd
# Ingest a folder with documents
docker compose exec rag-app python main.py ingest-dir ./data --recursive

# Or single file
docker compose exec rag-app python main.py ingest path/to/file.md

# Or multiple files
docker compose exec rag-app python main.py ingest-many file1.md file2.pdf file3.txt
```

#### From Web UI
1. Open http://localhost:5000
2. Click "Upload Documents"
3. Select folder or files
4. Click "Ingest"

#### From API
```bash
curl -X POST http://localhost:5000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{"directory": "path/to/docs", "recursive": true}'
```

---

### 3️⃣ Query Documents

#### From Web UI
1. Open http://localhost:5000
2. Type your question
3. Click "Ask"

#### From CLI
```cmd
docker compose exec rag-app python main.py query "What is machine learning?"
```

#### From API
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is RAG?", "top_k": 5}'
```

---

### 4️⃣ View Your Documents
```cmd
docker compose exec rag-app python main.py list
```

---

### 5️⃣ Remove a Document
```cmd
docker compose exec rag-app python main.py remove path/to/file.md
```

---

### 6️⃣ View Logs
```cmd
# Live logs
docker compose logs -f

# Last 50 lines
docker compose logs --tail 50

# Specific service
docker compose logs rag-app
```

---

### 7️⃣ Stop the App
```cmd
docker compose down

# Also remove volumes
docker compose down -v
```

---

## 🖥️ Windows Batch Script (rag.bat)

We created `rag.bat` for easy Windows access:

```cmd
# Use it like:
rag.bat start       # Start the app
rag.bat stop        # Stop the app
rag.bat logs        # View logs
rag.bat query       # Ask a question
rag.bat ingest      # Interactive ingest menu
rag.bat list        # List documents
rag.bat shell       # Open container bash
rag.bat build       # Rebuild image
```

---

## 🐧 Linux/Mac Shell Script (rag.sh)

We created `rag.sh` for Unix-like systems:

```bash
chmod +x rag.sh
./rag.sh start
./rag.sh query
./rag.sh ingest
# etc (same as rag.bat)
```

---

## 🌐 Deployment to Railway (Production)

See **RAILWAY.md** for full instructions.

Quick version:
```bash
npm install -g @railway/cli
railway login
railway init
railway variables set GROQ_API_KEY='your-key'
railway up
```

Your app will be live at: `https://your-app.railway.app`

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| **Container won't start** | `docker compose logs rag-app` → Check error message |
| **Port 5000 in use** | `docker compose down` → Kill existing instance |
| **No documents found** | Run: `docker compose exec rag-app python main.py ingest-dir ./data --recursive` |
| **GROQ_API_KEY error** | Check `.env` file has valid key from https://console.groq.com/keys |
| **Browser can't reach localhost:5000** | Make sure `docker compose up -d` succeeded. Check: `docker ps` |
| **Memory error** | Reduce `top_k` in queries or increase Docker RAM allocation |
| **Build takes too long** | First build downloads ML models (~1GB). Takes 5-10 min. Subsequent builds use cache. |

---

## 📊 Environment Variables

These control the app behavior. Set in `.env`:

```env
# Required
GROQ_API_KEY=gsk_AYn...         # Your API key

# Optional
GROQ_MODEL=openai/gpt-oss-120b  # LLM model
RAG_INDEX=rag_index             # Index folder path
FLASK_ENV=production            # production or development
PYTHONUNBUFFERED=1              # Unbuffered Python output
```

---

## 🔑 API Reference

All endpoints return JSON. Base URL: `http://localhost:5000/api`

### GET `/health`
Check if server is running.

```bash
curl http://localhost:5000/api/health
```

Response:
```json
{"status": "ok", "chunks": 42}
```

### GET `/docs`
List all ingested documents.

```bash
curl http://localhost:5000/api/docs
```

Response:
```json
{
  "documents": [
    {
      "doc_id": "1",
      "title": "My Document",
      "source": "path/to/file.md",
      "chunks": 10
    }
  ]
}
```

### POST `/ingest`
Add documents to the index.

```bash
curl -X POST http://localhost:5000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "data",
    "recursive": true
  }'
```

Body options:
- `{"directory": "path"}` — Ingest folder
- `{"files": ["a.md", "b.md"]}` — Specific files
- `{"text": "...", "source": "x"}` — Raw text

### POST `/query`
Ask a question.

```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is machine learning?",
    "top_k": 5
  }'
```

Response:
```json
{
  "answer": "Machine learning is...",
  "citations": {
    "1": {"title": "ML Basics", "source": "file.md"}
  },
  "confidence": "high",
  "chunks_used": 3
}
```

### DELETE `/remove`
Remove a document from the index.

```bash
curl -X DELETE http://localhost:5000/api/remove \
  -H "Content-Type: application/json" \
  -d '{"source": "path/to/file.md"}'
```

---

## 🎓 Example Workflow

```bash
# 1. Navigate to project
cd D:\BAI_TAP\code\vinvuong\rag_11

# 2. Start Docker
docker compose up -d

# 3. Prepare some documents in a folder
# Create folder: mkdir data
# Add files: copy docs/*.md data/

# 4. Ingest the documents
docker compose exec rag-app python main.py ingest-dir ./data --recursive

# 5. Ask questions
docker compose exec rag-app python main.py query "What is the main topic?"

# 6. View results in browser
# Open: http://localhost:5000

# 7. When done
docker compose down
```

---

## 💾 Persistence & Backups

The `rag_index/` folder contains your FAISS vector database. To back it up:

```bash
# Backup
copy rag_index rag_index_backup /S

# Restore
copy rag_index_backup rag_index /S
```

On Railway, this folder is automatically persisted in the container volume.

---

## 🚀 Next Steps

1. **Verify setup**: `docker compose up -d` → Open http://localhost:5000
2. **Add documents**: Put your `.md` or `.txt` files in a `data/` folder
3. **Ingest**: `docker compose exec rag-app python main.py ingest-dir ./data --recursive`
4. **Test queries**: Use the web UI or CLI
5. **Deploy to Railway**: Follow RAILWAY.md when ready
6. **Share the URL**: Your friends can use the deployed app 24/7

---

## 📞 Support

For issues:
- Check logs: `docker compose logs -f`
- Read DEPLOYMENT.md for detailed troubleshooting
- Check api_server.py line-by-line
- Verify GROQ_API_KEY is valid

---

## 📚 Full Documentation

- **QUICKREF.md** ← Quick commands reference
- **DEPLOYMENT.md** ← Full deployment guide with all options
- **RAILWAY.md** ← Production deployment to Railway cloud
- **Dockerfile** ← Container definition
- **docker-compose.yml** ← Local development config

---

## 🎉 You're All Set!

Your RAG-11 system is fully Dockerized and ready to deploy. Run:

```cmd
docker compose up -d
```

Then visit: **http://localhost:5000** 🚀

Questions? Check the docs or read the code comments in `api_server.py` and `main.py`.
