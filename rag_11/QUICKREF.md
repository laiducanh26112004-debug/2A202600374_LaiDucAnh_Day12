# RAG-11 Quick Reference Card

## Windows CMD - Fast Commands

```cmd
:: Start the app (creates + runs container in background)
docker compose up -d

:: View logs in real-time
docker compose logs -f

:: Stop the app
docker compose down

:: Build fresh image
docker build -t rag-11:latest .

:: SSH into container
docker compose exec rag-app bash

:: Run CLI command inside container
docker compose exec rag-app python main.py list
docker compose exec rag-app python main.py query "Your question"
docker compose exec rag-app python main.py ingest-dir data --recursive

:: View all containers
docker ps -a

:: Remove old images
docker rmi rag-11:latest
```

## Linux/Mac - Fast Commands

```bash
# Same commands as Windows CMD above (works on Linux/Mac too)
```

## API Endpoints (Once Server is Running)

### Check Health
```bash
curl http://localhost:5000/api/health
```

### List Documents
```bash
curl http://localhost:5000/api/docs
```

### Ingest Documents
```bash
curl -X POST http://localhost:5000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{"directory": "path/to/docs", "recursive": true}'
```

### Query
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is RAG?", "top_k": 5}'
```

---

## Directory Structure

```
rag_11/
├── api_server.py        ← Flask API (run this: python api_server.py)
├── main.py              ← CLI tool (run: python main.py [command])
├── Dockerfile           ← Container definition
├── docker-compose.yml   ← Compose config (run: docker compose up)
├── requirements.txt     ← Python dependencies
├── .env                 ← Secrets (GROQ_API_KEY)
├── rag_index/           ← FAISS vector index (persisted)
├── index.html           ← Web UI
└── DEPLOYMENT.md        ← Full guide
```

---

## Step-by-Step First Run

### 1. Prepare
```cmd
cd D:\BAI_TAP\code\vinvuong\rag_11
```

### 2. Start Docker Service
```cmd
docker --version
```
(Should show version, if not, start Docker Desktop)

### 3. Build Image
```cmd
docker build -t rag-11:latest .
```
(Takes 5-10 min first time, caches after)

### 4. Run with Docker Compose
```cmd
docker compose up -d
```

### 5. Wait 30 seconds, then open browser
```
http://localhost:5000
```

### 6. Add documents (in another CMD window)
```cmd
docker compose exec rag-app python main.py ingest-dir data --recursive
```

### 7. Test a query
```cmd
docker compose exec rag-app python main.py query "What is machine learning?"
```

### 8. Stop when done
```cmd
docker compose down
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Port 5000 already in use | `docker compose down` then `docker compose up -d` |
| Container won't start | `docker compose logs rag-app` (check error) |
| No documents found | Run `docker compose exec rag-app python main.py ingest-dir data --recursive` |
| GROQ_API_KEY error | Check `.env` file has valid key |
| Out of memory | Reduce `top_k` in queries or increase Docker RAM in settings |

---

## Railway Deployment (Production)

### Install Railway CLI
```bash
npm install -g @railway/cli
```

### Login & Deploy
```bash
railway login
railway init
railway variables set GROQ_API_KEY='your-key'
railway up
```

### Get Public URL
```bash
railway status
```

Your app will be live at: `https://your-app.railway.app`

---

## Environment Variables

Set these in Docker or locally:

| Variable | Example | Required |
|----------|---------|----------|
| `GROQ_API_KEY` | `gsk_AYn...` | Yes |
| `GROQ_MODEL` | `openai/gpt-oss-120b` | No (default) |
| `RAG_INDEX` | `rag_index` | No (default) |

Set in CMD:
```cmd
set GROQ_API_KEY=your-key-here
python api_server.py
```

Or in Docker:
```cmd
docker run -e GROQ_API_KEY='your-key' rag-11:latest
```

Or in `.env` file:
```
GROQ_API_KEY=your-key-here
```

---

## CLI Reference

### Ingest Commands
```bash
# Single file
python main.py ingest path/to/file.md --title "My Doc"

# Multiple files
python main.py ingest-many file1.md file2.md file3.txt

# Entire directory (recursive)
python main.py ingest-dir ./docs --recursive

# Glob pattern
python main.py ingest-glob "docs/**/*.md"
```

### Query & List
```bash
# Ask a question
python main.py query "What is AI?"

# List all documents
python main.py list

# Remove a document
python main.py remove path/to/file.md
```

### Within Container
```bash
docker compose exec rag-app python main.py [command]
```

---

## Performance Tips

1. **Pre-ingest before deployment** — Ingest all docs locally, then commit `rag_index/` to git
2. **Use volumes** — Persist `rag_index/` with `docker compose` volumes
3. **Adjust top_k** — Lower `top_k` = faster queries (trade-off: less context)
4. **Chunk size** — Larger chunks = fewer results, faster processing
5. **Use Railway for production** — Better uptime + auto-scaling than laptop

---

## File Locations

```
Logs:         docker compose logs -f
API URL:      http://localhost:5000
Web UI:       http://localhost:5000
Index:        ./rag_index/ (local)
Config:       .env
Docker image: rag-11:latest
```

---

## Key Files to Understand

| File | Purpose |
|------|---------|
| `api_server.py` | Flask REST API server |
| `main.py` | CLI interface for ingestion & querying |
| `ingestion.py` | Document loading & chunking |
| `retriever.py` | FAISS vector search |
| `reranker.py` | Re-ranks results by relevance |
| `generator.py` | Calls Groq LLM for answers |
| `context_builder.py` | Assembles retrieved chunks into context |

---

## Next Actions

- [ ] Ensure Docker Desktop is running
- [ ] Run `docker compose up -d`
- [ ] Open http://localhost:5000
- [ ] Ingest documents: `docker compose exec rag-app python main.py ingest-dir ./data --recursive`
- [ ] Test query endpoint
- [ ] Deploy to Railway when ready
