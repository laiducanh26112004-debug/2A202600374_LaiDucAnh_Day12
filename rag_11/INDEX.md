# RAG-11 Dockerization & Railway Deployment - Complete Guide

## ✅ What's Been Done

Your RAG-11 project is now **fully Dockerized** and ready for deployment. Here's what we've set up:

### 🐳 Docker Files Created
- **docker-compose.yml** — Local development setup (run with `docker compose up -d`)
- **Dockerfile** — Already present, multi-stage build (optimized)
- **.dockerignore** — Already present, excludes unnecessary files
- **railway.json** — Production deployment config for Railway

### 📚 Documentation Created
| File | Purpose |
|------|---------|
| **README_STARTUP.md** | ⭐ **START HERE** — Complete guide with examples |
| **QUICKREF.md** | Quick command reference for common tasks |
| **DEPLOYMENT.md** | Full deployment guide with all options |
| **RAILWAY.md** | How to deploy to Railway cloud (free) |
| **This file** | Index of all changes |

### 🛠️ Helper Scripts Created
| File | Purpose |
|------|---------|
| **SETUP.bat** | Interactive Windows setup wizard (run first on Windows) |
| **rag.bat** | Quick Windows command shortcuts |
| **rag.sh** | Quick Linux/Mac command shortcuts |

### 📝 Configuration Files
| File | Purpose |
|------|---------|
| **.env** | Your environment (contains GROQ_API_KEY) |
| **.env.example** | Template for team members |

---

## 🚀 Quick Start (Choose Your Path)

### 🎯 Beginner (Windows CMD) - Automated Setup
```cmd
cd D:\BAI_TAP\code\vinvuong\rag_11
SETUP.bat
```
This wizard will guide you through everything step-by-step.

---

### 🏃 Fast Start (Any OS) - 3 Commands
```cmd
cd D:\BAI_TAP\code\vinvuong\rag_11
docker compose up -d
start http://localhost:5000
```
That's it! Your app is running.

---

### ⚡ Experienced (Any OS) - Direct Commands

#### Start
```bash
docker compose up -d
```

#### Ingest Documents
```bash
docker compose exec rag-app python main.py ingest-dir ./data --recursive
```

#### Query
```bash
docker compose exec rag-app python main.py query "What is RAG?"
```

#### Stop
```bash
docker compose down
```

---

## 📖 Documentation Guide

### For First-Time Users
1. **Read**: `README_STARTUP.md` (13 min read) ⭐
2. **Run**: `SETUP.bat` (automated wizard)
3. **Test**: Open http://localhost:5000

### For Quick Reference
1. **Bookmark**: `QUICKREF.md` (1-page cheat sheet)
2. **Use**: When you need a command fast

### For Full Details
1. **Read**: `DEPLOYMENT.md` (full guide with troubleshooting)
2. **Use**: When setting up in production or diagnosing issues

### For Production/Cloud
1. **Read**: `RAILWAY.md` (deploy to cloud)
2. **Follow**: 3 options: Dashboard, CLI, or Git auto-deploy

---

## 🎯 How to Use Docker

### What is Docker?
Docker packages your app (code + dependencies) into a **container** — a lightweight virtual machine that runs anywhere.

### Why We're Using It
- ✅ **No installation headaches** — Everything pre-installed in the container
- ✅ **Same everywhere** — Works on Windows, Mac, Linux, and in the cloud
- ✅ **Easy to share** — Deploy to Railway with one command
- ✅ **Easy cleanup** — `docker compose down` removes everything

---

## 🔧 Basic Docker Commands

```bash
# Start the app (background)
docker compose up -d

# View live logs
docker compose logs -f

# Run a command inside the container
docker compose exec rag-app python main.py list

# Stop the app
docker compose down

# View running containers
docker ps

# View all containers (including stopped)
docker ps -a

# Remove an image
docker rmi rag-11:latest
```

---

## 📁 Project Structure

```
rag_11/
│
├─ 📚 DOCUMENTATION (Read these!)
│  ├─ README_STARTUP.md        ← Start here!
│  ├─ QUICKREF.md              ← Bookmark this
│  ├─ DEPLOYMENT.md            ← Full guide
│  ├─ RAILWAY.md               ← Cloud deployment
│  └─ INDEX.md                 ← This file
│
├─ 🐳 DOCKER SETUP (All configured!)
│  ├─ Dockerfile               ← Container definition
│  ├─ docker-compose.yml       ← Local dev config
│  ├─ railway.json             ← Cloud config
│  ├─ .dockerignore            ← What to exclude
│  ├─ .env                     ← Your secrets (GROQ_API_KEY)
│  └─ .env.example             ← Template
│
├─ 🛠️ HELPER SCRIPTS (Run on first use)
│  ├─ SETUP.bat                ← Windows wizard
│  ├─ rag.bat                  ← Windows shortcuts
│  └─ rag.sh                   ← Linux/Mac shortcuts
│
├─ 🐍 BACKEND CODE (Don't modify unless needed)
│  ├─ api_server.py            ← Main Flask app
│  ├─ main.py                  ← CLI tool
│  ├─ ingestion.py             ← Document processing
│  ├─ retriever.py             ← Vector search
│  ├─ reranker.py              ← Re-ranking
│  ├─ generator.py             ← LLM generation
│  ├─ context_builder.py       ← Context assembly
│  ├─ utils.py                 ← Utilities
│  └─ requirements.txt         ← Dependencies
│
├─ 🎨 FRONTEND (Web UI)
│  ├─ index.html               ← Web page
│  ├─ style.css                ← Styling
│  └─ script.js                ← Interactions
│
└─ 📊 DATA
   ├─ rag_index/               ← Vector database (auto-created)
   ├─ docker/                  ← Helper scripts
   └─ extras/                  ← Extra files
```

---

## 🎯 Typical Workflow

### Day 1: Setup & Test
```bash
# 1. Run setup wizard
SETUP.bat

# 2. Ingest sample documents
docker compose exec rag-app python main.py ingest-dir ./data --recursive

# 3. Test queries
docker compose exec rag-app python main.py query "What is this project about?"

# 4. Try web UI
# Open: http://localhost:5000
```

### Day 2+: Daily Use
```bash
# Start
docker compose up -d

# Ask questions via web UI or API
# http://localhost:5000

# Stop when done
docker compose down
```

### When Ready for Production
```bash
# Deploy to Railway
npm install -g @railway/cli
railway login
railway init
railway variables set GROQ_API_KEY='your-key'
railway up

# Your app is now live at: https://your-app.railway.app
```

---

## 🌐 Access Points

| What | Where |
|------|-------|
| **Web UI** | http://localhost:5000 |
| **API** | http://localhost:5000/api |
| **Health Check** | http://localhost:5000/api/health |
| **Production (Railway)** | https://your-app.railway.app |

---

## 🔑 Environment Variables

Your app needs the **GROQ_API_KEY** to work.

### Get Your Key
1. Go to: https://console.groq.com/keys
2. Create a new API key
3. Copy it

### Set It
In `.env` file:
```env
GROQ_API_KEY=gsk_your_actual_key_here
```

Or in Docker command:
```bash
docker run -e GROQ_API_KEY='your-key' rag-11:latest
```

---

## 📊 Files We Created

### Documentation
- ✅ README_STARTUP.md (13 KB)
- ✅ QUICKREF.md (6 KB)
- ✅ DEPLOYMENT.md (9 KB)
- ✅ RAILWAY.md (7 KB)
- ✅ INDEX.md (this file)

### Scripts
- ✅ SETUP.bat (7 KB) — Interactive setup wizard
- ✅ rag.bat (3 KB) — Windows shortcuts
- ✅ rag.sh (3 KB) — Linux/Mac shortcuts

### Configuration
- ✅ docker-compose.yml (0.6 KB) — Local dev setup
- ✅ railway.json (0.3 KB) — Cloud setup
- ✅ .env.example (0.4 KB) — Template

### Already Existed & Verified
- ✅ Dockerfile (multi-stage, optimized)
- ✅ .dockerignore (excludes cache, index)
- ✅ .env (with your GROQ_API_KEY)
- ✅ All Python source files
- ✅ Frontend (HTML/CSS/JS)

---

## ✨ Key Features

### 🔍 Hybrid Search
- **Dense**: FAISS vector similarity search
- **Sparse**: BM25 keyword search
- Combines both for better results

### 🎯 Reranking
- Re-ranks results by relevance
- Uses cross-encoder model

### 🤖 LLM Generation
- Uses Groq API (fast, free)
- Model: openai/gpt-oss-120b
- Generates answers with citations

### 🐳 Full Containerization
- Multi-stage Docker build (small images)
- Non-root user (security)
- Health checks
- Volume persistence

### ☁️ Cloud Ready
- Deploy to Railway in 1 command
- Auto-scaling
- Persistent storage
- 24/7 uptime

---

## 🚀 Next Steps

### Step 1: Run Setup (5 minutes)
```cmd
SETUP.bat
```

### Step 2: Add Your Documents
Put `.md` or `.txt` files in a `data/` folder, then:
```bash
docker compose exec rag-app python main.py ingest-dir ./data --recursive
```

### Step 3: Test
Open http://localhost:5000 and ask questions

### Step 4: Deploy (Optional)
When ready for production:
```bash
railway up
```

---

## 📞 Common Questions

**Q: Do I need to install Python?**
A: No! Docker includes everything. Docker Compose handles it all.

**Q: How big is the Docker image?**
A: ~2GB (includes Python, ML models, dependencies)

**Q: Can I run this on a laptop?**
A: Yes! Requires ~4GB RAM available. Increase Docker's memory limit if needed.

**Q: Does it work offline?**
A: No. Requires internet for:
- Groq API calls (for answers)
- Initial model downloads (one-time)

**Q: Can I modify the code?**
A: Yes! Edit Python files and rebuild: `docker build -t rag-11:latest .`

**Q: How do I backup my documents?**
A: The `rag_index/` folder contains everything. Backup this folder.

---

## 🆘 Troubleshooting Quick Links

- **Container won't start?** → See DEPLOYMENT.md "Troubleshooting" section
- **Port 5000 in use?** → Run `docker compose down` first
- **Out of memory?** → Reduce `top_k` in queries
- **No GROQ_API_KEY error?** → Check `.env` file
- **Can't connect to API?** → Ensure `docker compose up -d` succeeded

---

## 📚 Reading Order

For different roles:

### 👨‍💻 **Developer** (You're developing the app)
1. README_STARTUP.md
2. DEPLOYMENT.md → Troubleshooting section
3. Source code (api_server.py, main.py)

### 👤 **User** (You're using the app)
1. QUICKREF.md (just the commands)
2. README_STARTUP.md (if you get stuck)

### 🚀 **DevOps/Admin** (You're deploying to production)
1. DEPLOYMENT.md → Full guide
2. RAILWAY.md → Cloud deployment
3. Docker concepts (Google "Docker containers")

### 🎓 **Learning** (You want to understand everything)
1. README_STARTUP.md → Architecture section
2. DEPLOYMENT.md → Full guide
3. Docker documentation → https://docs.docker.com
4. Source code → Start with api_server.py

---

## 🎁 What You Can Do Now

✅ **Run locally** — `docker compose up -d`
✅ **Ingest documents** — `docker compose exec rag-app python main.py ingest-dir ./data --recursive`
✅ **Query via web UI** — Open http://localhost:5000
✅ **Query via API** — `curl http://localhost:5000/api/query`
✅ **Deploy to cloud** — `railway up` (Railway account required)
✅ **Share the app** — Deploy to Railway, share URL with friends
✅ **Modify code** — Edit Python files, rebuild: `docker build -t rag-11 .`
✅ **Backup** — Copy `rag_index/` folder

---

## 🎉 You're Ready!

Your RAG-11 system is:
- ✅ Fully Dockerized
- ✅ Ready to run locally
- ✅ Ready to deploy to Railway
- ✅ Documented for others

### Start here:
```bash
cd D:\BAI_TAP\code\vinvuong\rag_11
SETUP.bat
```

Or skip the wizard:
```bash
docker compose up -d
```

Then open: **http://localhost:5000**

---

## 📋 File Manifest

All files in rag_11/ directory:

### Documentation (NEW)
- README_STARTUP.md (⭐ Start here)
- QUICKREF.md (Bookmark this)
- DEPLOYMENT.md (Full guide)
- RAILWAY.md (Cloud deployment)
- INDEX.md (This file)

### Scripts (NEW)
- SETUP.bat (Windows wizard)
- rag.bat (Windows shortcuts)
- rag.sh (Linux/Mac shortcuts)

### Config (NEW or UPDATED)
- docker-compose.yml (NEW - for local dev)
- railway.json (NEW - for cloud)
- .env.example (NEW - template)
- .env (already present with your API key)

### Existing (Verified Ready)
- Dockerfile
- .dockerignore
- All Python source files
- All frontend files
- requirements.txt

---

## ✅ Deployment Checklist

- [x] Docker setup created
- [x] docker-compose.yml configured
- [x] Documentation written (5 guides)
- [x] Helper scripts created (3 scripts)
- [x] Environment template created
- [x] Railway config created
- [x] Dockerfile verified (multi-stage, optimized)
- [x] This index created

**Status: READY TO DEPLOY** ✅

---

## 🎯 Last Step

Choose your path:

### 🏃 **Just want to run it?**
```bash
docker compose up -d
# Open: http://localhost:5000
```

### 📖 **Want to learn first?**
Read: `README_STARTUP.md`

### 🚀 **Want to deploy to cloud?**
Read: `RAILWAY.md`

### 🎓 **Want full documentation?**
See: `DEPLOYMENT.md`

---

**You're all set! Your RAG-11 is Dockerized and ready to ship.** 🚀
