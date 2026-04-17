# RAG-11 Deployment & CLI Guide

## Quick Start (Local Development)

### Prerequisites
- Docker & Docker Compose installed
- Python 3.11+ (for local CLI)
- GROQ_API_KEY from [https://console.groq.com](https://console.groq.com)

### 1. Setup Environment
```bash
cd D:/BAI_TAP/code/vinvuong/rag_11

# Copy .env template (if needed)
# Already present with GROQ_API_KEY
```

### 2. Run with Docker Compose (Recommended)
```bash
# Start the app in the background
docker compose up -d

# View logs
docker compose logs -f

# Stop the app
docker compose down
```

**Access the app:** http://localhost:5000

### 3. Manual Docker Build & Run
```bash
# Build the image
docker build -t rag-11:latest .

# Run the container
docker run -d \
  -p 5000:5000 \
  -e GROQ_API_KEY='your-key-here' \
  -v $(pwd)/rag_index:/app/rag_index \
  --name rag_11_app \
  rag-11:latest

# View logs
docker logs -f rag_11_app

# Stop the container
docker stop rag_11_app
docker rm rag_11_app
```

### 4. Run Locally (without Docker)
```bash
# Install dependencies
pip install -r requirements.txt

# Set GROQ_API_KEY in terminal
# Windows (PowerShell)
$env:GROQ_API_KEY = 'your-key-here'

# Windows (CMD)
set GROQ_API_KEY=your-key-here

# Linux/Mac
export GROQ_API_KEY='your-key-here'

# Run the Flask server
python api_server.py

# In another terminal, run CLI commands (see below)
python main.py list
python main.py ingest-dir ./docs
python main.py query "What is RAG?"
```

---

## Command Line Interface (CLI)

All commands assume you're in the `rag_11` directory and have the environment set up.

### Ingest Documents

#### Ingest a Single File
```bash
python main.py ingest path/to/document.md --title "My Document"
```

#### Ingest Multiple Files
```bash
python main.py ingest-many file1.md file2.md file3.txt
python main.py ingest-many *.md file.txt  # Glob patterns work too
```

#### Ingest Entire Directory
```bash
# Non-recursive (only direct children)
python main.py ingest-dir ./docs

# Recursive (all subdirectories)
python main.py ingest-dir ./docs --recursive

# Custom file extensions
python main.py ingest-dir ./docs --ext .md .txt .pdf --recursive
```

#### Ingest with Glob Patterns
```bash
python main.py ingest-glob "docs/**/*.md"
python main.py ingest-glob "src/**/*.py"
```

### Query Documents

#### Ask a Question
```bash
python main.py query "What is machine learning?"

# With custom retrieval size
python main.py query "Explain RAG" --top-k 10
```

### Manage Documents

#### List All Ingested Documents
```bash
python main.py list
```

#### Remove a Document
```bash
python main.py remove path/to/document.md
```

---

## Docker Commands Reference

### Building
```bash
# Build with tag
docker build -t rag-11:latest .

# Build without cache (fresh)
docker build --no-cache -t rag-11:latest .

# Build and tag multiple versions
docker build -t rag-11:v1.0 -t rag-11:latest .
```

### Running
```bash
# Run detached (background)
docker run -d -p 5000:5000 --name rag_11_app rag-11:latest

# Run with environment file
docker run -d -p 5000:5000 --env-file .env --name rag_11_app rag-11:latest

# Run with persistent volumes
docker run -d \
  -p 5000:5000 \
  -v $(pwd)/rag_index:/app/rag_index \
  -v $(pwd)/data:/app/data \
  --env-file .env \
  --name rag_11_app \
  rag-11:latest

# Run interactively (foreground)
docker run -it -p 5000:5000 rag-11:latest
```

### Container Management
```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# View logs
docker logs rag_11_app
docker logs -f rag_11_app  # Follow logs
docker logs --tail 100 rag_11_app  # Last 100 lines

# Execute command in running container
docker exec -it rag_11_app bash
docker exec rag_11_app python main.py list

# Stop container
docker stop rag_11_app

# Start stopped container
docker start rag_11_app

# Remove container
docker rm rag_11_app

# Remove image
docker rmi rag-11:latest
```

### Docker Compose Commands
```bash
# Start services
docker compose up
docker compose up -d  # Detached

# Rebuild image before starting
docker compose up -d --build

# View running services
docker compose ps

# View logs
docker compose logs -f

# Execute command in service
docker compose exec rag-app python main.py list

# Stop services
docker compose down

# Stop and remove volumes
docker compose down -v

# Restart services
docker compose restart
```

---

## Deployment to Railway

### Prerequisites
- Railway account ([https://railway.app](https://railway.app))
- Railway CLI installed: `npm install -g @railway/cli`

### Steps

#### 1. Login to Railway
```bash
railway login
```

#### 2. Create a New Project
```bash
railway init
# Follow the prompts to create a new project
```

#### 3. Link to Your Repository (Optional)
```bash
# If using Git
git init
git add .
git commit -m "Initial RAG-11 commit"
git remote add origin https://github.com/yourusername/rag-11.git
git push -u origin main
```

#### 4. Set Environment Variables
```bash
railway variables set GROQ_API_KEY='your-api-key'
railway variables set GROQ_MODEL='openai/gpt-oss-120b'
railway variables set RAG_INDEX='rag_index'
```

#### 5. Deploy
```bash
railway up
```

#### 6. View Deployment
```bash
# Get the URL
railway status

# View logs
railway logs

# Access your app: https://your-railway-url.railway.app
```

#### Update After Changes
```bash
git push origin main
# Railway auto-deploys on push if linked to GitHub

# Or manual deploy
railway up
```

### Railway Dashboard
- Go to [https://railway.app/dashboard](https://railway.app/dashboard)
- View logs, environment variables, and deployment history
- Configure custom domain

---

## API Endpoints

### Health Check
```bash
curl http://localhost:5000/api/health
```

### List Documents
```bash
curl http://localhost:5000/api/docs
```

### Ingest Documents
```bash
# From directory
curl -X POST http://localhost:5000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{"directory": "path/to/docs", "recursive": true}'

# From files
curl -X POST http://localhost:5000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{"files": ["file1.md", "file2.md"]}'

# From raw text
curl -X POST http://localhost:5000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{"text": "Some content", "source": "raw-input", "title": "My Doc"}'
```

### Query
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is RAG?", "top_k": 5}'
```

### Remove Document
```bash
curl -X DELETE http://localhost:5000/api/remove \
  -H "Content-Type: application/json" \
  -d '{"source": "path/to/document.md"}'
```

---

## Troubleshooting

### Container won't start
```bash
# Check logs
docker compose logs rag-app

# Check if port 5000 is in use
netstat -ano | findstr :5000  # Windows
lsof -i :5000  # Linux/Mac
```

### API returns "No documents ingested"
- Ingest documents first: `python main.py ingest-dir ./docs`
- Or use POST `/api/ingest` endpoint

### GROQ_API_KEY not found
- Ensure `.env` file exists with `GROQ_API_KEY='...'`
- Or set in terminal before running
- Check Docker: `docker exec rag_11_app env | grep GROQ`

### Out of memory
- Reduce `chunk_size` in `main.py` (line 28)
- Limit `top_k` in queries
- Use Docker memory limits: `docker run -m 2g ...`

---

## File Structure
```
rag_11/
├── api_server.py          # Flask API server
├── main.py                # CLI interface
├── ingestion.py           # Document ingestion
├── retriever.py           # Retrieval logic
├── reranker.py            # Reranking module
├── context_builder.py     # Context assembly
├── generator.py           # LLM generation
├── utils.py               # Utilities
├── Dockerfile             # Container definition
├── docker-compose.yml     # Compose configuration
├── railway.json           # Railway config
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── .dockerignore          # Docker ignore rules
├── rag_index/             # FAISS index (persisted)
├── index.html             # Frontend
├── style.css              # Styles
├── script.js              # Frontend JS
└── DEPLOYMENT.md          # This file
```

---

## Performance Tips

1. **Use multi-stage Dockerfile** (already done) — reduces image size
2. **Persist `rag_index/`** via volumes — avoids re-indexing
3. **Pre-ingest documents** — before deploying to Railway
4. **Increase chunk size** — for fewer but larger context windows
5. **Adjust `top_k`** — lower values = faster queries
6. **Use Railway caching** — for faster deployments

---

## Next Steps

- [ ] Add your documents to `data/` folder
- [ ] Ingest them: `python main.py ingest-dir ./data --recursive`
- [ ] Test locally: `docker compose up`
- [ ] Deploy to Railway: `railway up`
- [ ] Share the Railway URL with users
- [ ] Monitor logs: `railway logs`
