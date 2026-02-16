# Airo Bid Evaluation Platform - Deployment Guide

Complete instructions for deploying the Airo Bid Evaluation Platform to cloud platforms.

---

## 📋 Prerequisites

- Python 3.10+
- Git
- Anthropic API key (from https://console.anthropic.com)
- Cloud platform account (Streamlit Cloud, Heroku, AWS, etc.)

---

## 🚀 Option 1: Streamlit Cloud (Recommended - Easiest)

### Step 1: Prepare Repository
```bash
git init
git add .
git commit -m "Initial commit: Airo Bid Evaluation Platform"
git remote add origin https://github.com/YOUR_USERNAME/bid-eval-demo.git
git push -u origin main
```

### Step 2: Set Up Streamlit Cloud
1. Go to https://streamlit.io/cloud
2. Click **"New app"**
3. Select your GitHub repository
4. Choose branch: `main`
5. Set file path: `app.py`
6. Click **"Deploy"**

### Step 3: Add API Key as Secret
1. In Streamlit Cloud dashboard, go to your app
2. Click **⋯** (menu) → **"Settings"**
3. Click **"Secrets"**
4. Add your secret:
   ```
   ANTHROPIC_API_KEY = "sk-ant-your-api-key-here"
   ```
5. Save

### Step 4: Redeploy
- Click **"Rerun"** to apply secrets
- App will be live at: `https://your-app-name.streamlit.app`

**Pros:**
- Free tier available
- Automatic deployments from GitHub
- Easy secret management
- Built-in SSL/HTTPS

**Cons:**
- Limited to 1GB memory
- Limited to 1GB storage
- May have cold start delays

---

## 🐳 Option 2: Docker + Heroku

### Prerequisites
- Docker installed locally
- Heroku CLI installed
- Heroku account with app created

### Step 1: Create Heroku App
```bash
heroku login
heroku create your-app-name
```

### Step 2: Set Environment Variables
```bash
heroku config:set ANTHROPIC_API_KEY="sk-ant-your-api-key-here"
```

### Step 3: Deploy with Docker
```bash
# Log in to Heroku container registry
heroku container:login

# Build and push Docker image
heroku container:push web

# Release the image
heroku container:release web

# View logs
heroku logs --tail
```

### Step 4: Access App
```bash
heroku open
```

**Pros:**
- More control over environment
- Standard deployment workflow
- Free tier available

**Cons:**
- Heroku free tier ending (as of Nov 2022)
- Requires Docker knowledge
- Manual deployment steps

---

## ☁️ Option 3: AWS (EC2 + Docker)

### Step 1: Launch EC2 Instance
1. Go to AWS EC2 Dashboard
2. Click **"Launch Instance"**
3. Select **Ubuntu 22.04 LTS** (or latest)
4. Instance type: `t3.small` (or larger for production)
5. Create/select security group allowing:
   - Port 80 (HTTP)
   - Port 443 (HTTPS)
   - Port 22 (SSH)
6. Launch instance

### Step 2: SSH into Instance
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### Step 3: Install Docker
```bash
sudo apt update
sudo apt install -y docker.io git
sudo usermod -aG docker ubuntu
```

### Step 4: Clone and Run
```bash
git clone https://github.com/YOUR_USERNAME/bid-eval-demo.git
cd bid-eval-demo

# Set environment variable
export ANTHROPIC_API_KEY="sk-ant-your-api-key-here"

# Build and run Docker container
docker build -t bid-eval-demo .
docker run -p 80:8501 \
  -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  bid-eval-demo
```

### Step 5: Set Up HTTPS with Let's Encrypt
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot certonly -d your-domain.com
```

**Pros:**
- Full control
- Scalable
- Cost-effective

**Cons:**
- Requires DevOps knowledge
- Manual maintenance required

---

## 🔷 Option 4: Google Cloud Run

### Step 1: Set Up Google Cloud
```bash
gcloud init
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### Step 2: Build and Push to Container Registry
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/bid-eval-demo
```

### Step 3: Deploy to Cloud Run
```bash
gcloud run deploy bid-eval-demo \
  --image gcr.io/YOUR_PROJECT_ID/bid-eval-demo \
  --platform managed \
  --region us-central1 \
  --memory 1Gi \
  --set-env-vars ANTHROPIC_API_KEY=sk-ant-your-api-key-here \
  --allow-unauthenticated
```

**Pros:**
- Fully managed
- Auto-scaling
- Pay-per-use pricing

**Cons:**
- More expensive than other options
- Vendor lock-in

---

## 📱 Option 5: Azure Container Instances

### Step 1: Create Resource Group
```bash
az group create --name bid-eval-rg --location eastus
```

### Step 2: Create Container Registry
```bash
az acr create --resource-group bid-eval-rg \
  --name bidevalregistry \
  --sku Basic
```

### Step 3: Build and Push Image
```bash
az acr build --registry bidevalregistry \
  --image bid-eval-demo:latest .
```

### Step 4: Deploy Container
```bash
az container create \
  --resource-group bid-eval-rg \
  --name bid-eval-container \
  --image bidevalregistry.azurecr.io/bid-eval-demo:latest \
  --ports 8501 \
  --environment-variables ANTHROPIC_API_KEY=sk-ant-your-api-key-here \
  --dns-name-label bid-eval-demo \
  --registry-login-server bidevalregistry.azurecr.io
```

---

## 🔐 Security Best Practices

### 1. **Environment Variables**
- ✅ Use secrets management (not in code)
- ❌ Never commit API keys to GitHub

### 2. **API Rate Limiting**
Add to your app to prevent abuse:
```python
# In utils/ai_engine.py
import time
from functools import wraps

def rate_limit(calls=100, period=60):
    """Rate limit decorator"""
    min_interval = period / calls
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator
```

### 3. **CORS Settings**
Configure in `.streamlit/config.toml`:
```toml
[server]
enableCORS = true
enableXsrfProtection = true
```

### 4. **SSL/HTTPS**
- Always use HTTPS in production
- Use Let's Encrypt (free)
- Or cloud provider's built-in SSL

### 5. **Logging & Monitoring**
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Tender processed: {tender_title}")
logger.warning(f"API rate limit approaching")
logger.error(f"Failed to evaluate bid: {error}")
```

---

## 📊 Monitoring & Logs

### Streamlit Cloud
- View logs in Streamlit Cloud dashboard
- Real-time monitoring available

### Heroku
```bash
heroku logs --tail
heroku logs --num 50
```

### Docker (Local)
```bash
docker logs -f container-id
```

### AWS CloudWatch
1. Go to CloudWatch dashboard
2. Select your log group
3. View real-time logs

---

## 🔄 CI/CD Pipeline (GitHub Actions)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Streamlit Cloud

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Trigger Streamlit Cloud Deploy
      run: |
        curl -X POST \
          -H "Authorization: Bearer ${{ secrets.STREAMLIT_API_TOKEN }}" \
          https://api.streamlit.io/v1/repos/deploy \
          -d '{"repository": "github_username/bid-eval-demo"}'
```

---

## 📈 Scaling Considerations

### For 100+ concurrent users:
1. **Use Docker + Kubernetes** (EKS, GKE, AKS)
2. **Add load balancing**
3. **Use CDN for static assets**
4. **Implement caching layer** (Redis)
5. **Scale API calls** with async processing

### For high API usage:
1. **Implement request queuing**
2. **Use background workers** (Celery, RQ)
3. **Cache Claude responses**
4. **Add rate limiting per user**

---

## ✅ Pre-Deployment Checklist

- [ ] API key configured as secret (not in code)
- [ ] `.env` file NOT committed to git
- [ ] `.gitignore` includes sensitive files
- [ ] All dependencies in `requirements.txt`
- [ ] App tested locally: `streamlit run app.py`
- [ ] Logo file (AiroLogo.png) included
- [ ] README.md updated
- [ ] Health checks configured
- [ ] Logging enabled
- [ ] CORS settings configured

---

## 🆘 Troubleshooting

### App Won't Start
```bash
# Check logs
streamlit run app.py --logger.level=debug

# Verify dependencies
pip install -r requirements.txt --upgrade
```

### API Key Not Found
```bash
# Streamlit Cloud: Check Secrets in settings
# Docker: Set env variable
export ANTHROPIC_API_KEY="your-key"

# Local: Create .env file
echo "ANTHROPIC_API_KEY=your-key" > .env
```

### Out of Memory
- Increase instance size
- Clear old sessions: `st.cache_data.clear()`
- Use streaming for large responses

### Slow Performance
- Enable caching: `@st.cache_data`
- Use CDN for static files
- Optimize PDF processing
- Add database for persistent storage

---

## 📞 Support

- **Streamlit Docs**: https://docs.streamlit.io/
- **Anthropic API**: https://docs.anthropic.com/
- **Docker**: https://docs.docker.com/
- **Heroku**: https://devcenter.heroku.com/

---

## 🚀 Next Steps

1. Choose deployment platform
2. Follow the instructions above
3. Set up monitoring and logging
4. Implement CI/CD pipeline
5. Test with real users
6. Monitor performance and costs

---

**Last Updated**: February 2026
**Version**: 1.0.0
