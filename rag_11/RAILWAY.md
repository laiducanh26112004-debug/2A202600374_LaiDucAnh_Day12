# Deploy RAG-11 to Railway

## What is Railway?

Railway is a PaaS (Platform-as-a-Service) that makes deploying Docker apps simple. Your RAG app will run on Railway's servers instead of your laptop, making it available 24/7 via a public URL.

---

## Prerequisites

1. **Railway account** — Sign up free at https://railway.app
2. **Railway CLI** — Install with `npm install -g @railway/cli`
3. **Git** (optional but recommended) — For easier deployment

---

## Option 1: Deploy via Railway Dashboard (Easiest)

### Step 1: Create a New Project on Railway
1. Go to https://railway.app/dashboard
2. Click **+ New Project**
3. Select **Deploy from GitHub** (or **Empty Project** if using CLI)

### Step 2: Connect Your GitHub Repository
1. Select your GitHub account
2. Search for `rag-11` or your repo name
3. Click **Connect Repository**

### Step 3: Set Environment Variables
1. In Railway dashboard, go to **Variables**
2. Add:
   ```
   GROQ_API_KEY = your-actual-api-key
   GROQ_MODEL = openai/gpt-oss-120b
   RAG_INDEX = rag_index
   PORT = 5000
   ```

### Step 4: Deploy
1. Click **Deploy**
2. Wait for build to complete (5-10 minutes)
3. Once green, your app is live

### Step 5: Get Your URL
1. In Railway, click on your service
2. Under **Domains**, copy the public URL
3. Visit `https://your-app.railway.app` in your browser

---

## Option 2: Deploy via Railway CLI (Faster)

### Step 1: Login
```bash
railway login
```
(Opens browser to authenticate)

### Step 2: Initialize Railway Project
```bash
cd D:\BAI_TAP\code\vinvuong\rag_11
railway init
# Select your team/organization
# Name the project "rag-11"
```

### Step 3: Set Environment Variables
```bash
railway variables set GROQ_API_KEY='your-actual-key-here'
railway variables set GROQ_MODEL='openai/gpt-oss-120b'
railway variables set RAG_INDEX='rag_index'
```

### Step 4: Deploy
```bash
railway up
```

The CLI will:
- Build your Docker image
- Upload to Railway
- Start the container
- Display your public URL

### Step 5: View Logs
```bash
railway logs
```

### Step 6: Get Status
```bash
railway status
```

---

## Option 3: Deploy via Git Push (Automatic)

### Step 1: Connect GitHub
```bash
git init
git add .
git commit -m "Initial RAG-11 commit"
git remote add origin https://github.com/yourusername/rag-11.git
git push -u origin main
```

### Step 2: Connect Railway to GitHub
1. Go to https://railway.app/dashboard
2. Click **+ New Project**
3. Select **Deploy from GitHub**
4. Search for your repo
5. Click **Deploy**

### Step 3: Set Environment Variables in Railway
(Same as Option 1, Step 3)

### Step 4: Auto-Deploy on Push
From now on, every `git push` auto-deploys your changes:
```bash
git add .
git commit -m "Updated RAG"
git push  # Automatically redeploys
```

---

## Verify Deployment

Once Railway shows a green checkmark, test your API:

```bash
# Test health endpoint
curl https://your-app.railway.app/api/health

# Test web UI
# Open in browser: https://your-app.railway.app

# Test ingestion (from your laptop)
curl -X POST https://your-app.railway.app/api/ingest \
  -H "Content-Type: application/json" \
  -d '{"directory": "data", "recursive": true}'

# Test query
curl -X POST https://your-app.railway.app/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is RAG?", "top_k": 5}'
```

---

## Update Your App on Railway

### Option A: CLI (Fastest)
```bash
# From your local directory
railway up
```

### Option B: Git Push (Auto)
```bash
git add .
git commit -m "Fixed bug"
git push origin main
# Railway redeploys automatically in 2-3 minutes
```

### Option C: Railway Dashboard (Manual)
1. Go to https://railway.app/dashboard
2. Click your project
3. Click **Redeploy**

---

## Manage Your Deployment

### View Logs
```bash
railway logs
# Or in dashboard: click service → Logs tab
```

### Stop the App
```bash
railway down
# Or in dashboard: click service → Settings → Delete
```

### View Metrics
1. Go to Railway dashboard
2. Click your service
3. Check **Metrics** tab for CPU/Memory usage

### Restart
```bash
railway restart
# Or in dashboard: click service → Settings → Restart
```

---

## Pricing

- **Free tier**: 5 projects, 500GB bandwidth, 100GB storage (per month)
- **Pro**: $5/month + usage costs
- **Enterprise**: Custom pricing

Your RAG app likely stays within free tier if you pre-ingest documents locally and only serve queries on Railway.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Build fails | Check logs: `railway logs` or dashboard Logs tab |
| App crashes | Check GROQ_API_KEY is valid and set in Variables |
| Port not responding | Ensure Dockerfile exposes port 5000 (it does) |
| Out of memory | Railway free tier has 1GB RAM. Add more with Pro tier. |
| Disk space full | Delete old `rag_index` files or use Pro tier (20GB storage) |

### Debug Commands
```bash
# See exact error
railway logs -f

# Check environment
railway shell
# Inside shell: env | grep GROQ

# Test locally first
docker compose up  # Test locally before deploying
```

---

## Cost Estimation

| Action | Cost |
|--------|------|
| Storing 1000 documents | ~50MB (free) |
| 100 queries/day | ~10GB bandwidth/month (free) |
| 10,000 queries/month | $2-5 in usage (depends on model) |
| Running 24/7 | Free tier or $5/month Pro |

**Recommendation**: Use free tier for testing, upgrade to Pro once live.

---

## Best Practices

1. **Pre-ingest documents locally** — Reduces Railway build time
2. **Use volumes for persistence** — Railway persists `rag_index/` automatically
3. **Monitor logs** — `railway logs` to catch errors early
4. **Set up auto-deploy** — Use GitHub integration for auto-updates
5. **Backup GROQ API key** — Store safely, don't commit to git
6. **Use `.env.example`** — Template for team members
7. **Set resource limits** — Pro tier: limit memory to prevent runaway costs

---

## Connect a Custom Domain (Optional)

### Add Custom Domain
1. In Railway dashboard, click your service
2. Go to **Domains**
3. Click **+ New Domain**
4. Enter your domain (e.g., `rag.yourdomain.com`)
5. Update your DNS settings (CNAME to Railway's provided URL)

---

## Next Steps

- [ ] Sign up at https://railway.app
- [ ] Install Railway CLI: `npm install -g @railway/cli`
- [ ] Run `railway login`
- [ ] Run `railway init` in your rag_11 directory
- [ ] Set GROQ_API_KEY and deploy
- [ ] Share the URL with your team
- [ ] Monitor with `railway logs`

Your RAG-11 is now live and shareable 🚀
