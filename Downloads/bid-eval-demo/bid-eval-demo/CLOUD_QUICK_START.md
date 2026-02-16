# ☁️ Cloud Deployment Quick Start

Choose your platform and follow the quick steps below.

---

## 🟢 Streamlit Cloud (Easiest - Recommended)

**Time to deploy**: 5 minutes | **Cost**: Free tier available | **Difficulty**: ⭐

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Deploy Airo Bid Evaluation Platform"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/bid-eval-demo.git
git push -u origin main
```

### 2. Deploy on Streamlit Cloud
- Go to https://streamlit.io/cloud
- Click **"New app"**
- Select your GitHub repo, branch `main`, file `app.py`
- Click **"Deploy"**

### 3. Add API Secret
1. Click **⋯** → **Settings**
2. Click **Secrets**
3. Add:
   ```
   ANTHROPIC_API_KEY = "sk-ant-xxx..."
   ```
4. Click **Rerun**

✅ **Done!** App live at `https://your-app.streamlit.app`

---

## 🐳 Docker + Heroku

**Time to deploy**: 15 minutes | **Cost**: Free tier ending | **Difficulty**: ⭐⭐

### 1. Install & Login
```bash
# Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli
heroku login
heroku create your-unique-app-name
```

### 2. Deploy
```bash
# Option A: Using Git
git push heroku main

# Option B: Using Docker
heroku container:login
heroku container:push web
heroku container:release web
```

### 3. Set Environment Variable
```bash
heroku config:set ANTHROPIC_API_KEY="sk-ant-xxx..."
heroku open
```

✅ **Done!** App live at `https://your-unique-app-name.herokuapp.com`

---

## ☁️ Google Cloud Run

**Time to deploy**: 20 minutes | **Cost**: Pay per use | **Difficulty**: ⭐⭐

### 1. Install & Setup
```bash
# Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install
gcloud init
gcloud auth login
```

### 2. Create Project & Deploy
```bash
gcloud config set project YOUR_PROJECT_ID

gcloud run deploy bid-eval-demo \
  --source . \
  --region us-central1 \
  --memory 1Gi \
  --set-env-vars ANTHROPIC_API_KEY=sk-ant-xxx... \
  --allow-unauthenticated
```

✅ **Done!** App URL shown in terminal output

---

## 🟦 Microsoft Azure

**Time to deploy**: 20 minutes | **Cost**: Free tier available | **Difficulty**: ⭐⭐

### 1. Install & Setup
```bash
# Install Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
az login
az group create --name bid-eval-rg --location eastus
```

### 2. Create Registry & Deploy
```bash
az acr create --resource-group bid-eval-rg \
  --name bidevalregistry --sku Basic

az acr build --registry bidevalregistry \
  --image bid-eval:latest .

az container create \
  --resource-group bid-eval-rg \
  --name bid-eval \
  --image bidevalregistry.azurecr.io/bid-eval:latest \
  --ports 8501 \
  --environment-variables ANTHROPIC_API_KEY=sk-ant-xxx... \
  --dns-name-label bid-eval-demo \
  --registry-login-server bidevalregistry.azurecr.io
```

✅ **Done!** Access at `http://bid-eval-demo.eastus.azurecontainer.io:8501`

---

## 🔴 AWS (EC2 + Docker)

**Time to deploy**: 30 minutes | **Cost**: Free tier available | **Difficulty**: ⭐⭐⭐

### 1. Launch EC2 Instance
- Go to AWS EC2 Dashboard
- Launch Instance → Ubuntu 22.04 LTS → t3.small
- Create security group allowing ports 22, 80, 443
- Download `.pem` key file

### 2. Connect & Deploy
```bash
# SSH into instance
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# Install Docker
sudo apt update && sudo apt install -y docker.io git
sudo usermod -aG docker ubuntu && exit

# Reconnect
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# Clone & Run
git clone https://github.com/YOUR_USERNAME/bid-eval-demo.git
cd bid-eval-demo

docker build -t bid-eval .
docker run -p 80:8501 \
  -e ANTHROPIC_API_KEY="sk-ant-xxx..." \
  bid-eval
```

✅ **Done!** Access at `http://YOUR_EC2_IP:80`

---

## 🐳 Docker (Local Testing)

**Time to run**: 2 minutes | **Cost**: Free | **Difficulty**: ⭐

### 1. Build & Run
```bash
# Requires Docker installed

docker build -t bid-eval-demo .

docker run -p 8501:8501 \
  -e ANTHROPIC_API_KEY="sk-ant-xxx..." \
  bid-eval-demo
```

Access at `http://localhost:8501`

### 2. With Docker Compose
```bash
export ANTHROPIC_API_KEY="sk-ant-xxx..."
docker-compose up
```

---

## 🔐 API Key Security

### ❌ DO NOT:
- Commit API keys to GitHub
- Put API keys in code
- Share API keys in slack/email

### ✅ DO:
- Use platform secrets/environment variables
- Create separate keys for dev/prod
- Rotate keys regularly
- Use secrets manager (Vault, Secrets Manager)

### How to Add Secrets:

**Streamlit Cloud**: Dashboard → App Settings → Secrets
**Heroku**: `heroku config:set KEY=VALUE`
**Docker**: `-e KEY=VALUE` or `.env` file
**Cloud Run**: `--set-env-vars KEY=VALUE`
**EC2**: Export in shell or use `.env`

---

## 📋 Platform Comparison

| Feature | Streamlit Cloud | Heroku | Google Cloud | Azure | AWS |
|---------|-----------------|--------|--------------|-------|-----|
| Setup Time | 5 min | 15 min | 20 min | 20 min | 30 min |
| Difficulty | ⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Free Tier | Yes | No | Yes | Yes | Yes |
| Cost/Month | Free | $50+ | $2-20 | $2-20 | $2-30 |
| Scaling | Auto | Manual | Auto | Auto | Manual |
| Maintenance | None | Minimal | Minimal | Minimal | High |

---

## ✅ Post-Deployment

After deploying, verify:

- [ ] App loads without errors
- [ ] Can upload tender document
- [ ] Can evaluate bids
- [ ] Dashboard displays charts
- [ ] Can download reports
- [ ] Chat is responsive
- [ ] Logo displays correctly
- [ ] API calls working
- [ ] No error logs

---

## 🆘 Common Issues

### "API key not found"
```bash
# Verify secret is set
heroku config:get ANTHROPIC_API_KEY
gcloud run services describe SERVICE_NAME
az container show -g RESOURCE_GROUP -n CONTAINER_NAME
```

### "Port 8501 already in use"
```bash
# Use different port
streamlit run app.py --server.port 8502

# Docker:
docker run -p 8502:8501 bid-eval-demo
```

### "Out of memory"
- Increase instance size
- Use smaller model: `claude-3-5-haiku-20241022`
- Enable caching in app

### "Slow uploads"
- Check file size (max 100MB)
- Use cloud storage for large files
- Add progress indicators

---

## 📞 Get Help

- **Streamlit**: https://discuss.streamlit.io/
- **Anthropic**: https://support.anthropic.com/
- **Platform Docs**: See DEPLOYMENT.md

---

## 🚀 What's Next

1. ✅ Choose a platform above
2. ✅ Follow 3-4 simple steps
3. ✅ Share app URL with stakeholders
4. ✅ Monitor usage and performance
5. ✅ Collect feedback and iterate

**Recommended**: Start with Streamlit Cloud for easiest deployment! 🟢
