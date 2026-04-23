# Student Feedback Sentiment Analysis (AI-Powered)

This project analyzes student feedback using NLP (VADER/DistilBERT) and provides an interactive dashboard for visualized reports.

## 🚀 One-Click Deployment (Recommended)

### 1. Deploy the Backend (Python/FastAPI)
1. Go to [Render.com](https://render.com) and create a new **Web Service**.
2. Connect this GitHub repository.
3. Use the following settings:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
   - **Root Directory**: `backend`
4. Once deployed, copy your **Web Service URL** (e.g., `https://sentiment-api.onrender.com`).

### 2. Deploy the Frontend (HTML/JS)
1. In `frontend/index.html`, update the `API` constant on line 301 to your new Backend URL.
2. Go to Render or Vercel and create a new **Static Site**.
3. Use the following settings:
   - **Build Command**: (leave empty)
   - **Publish Directory**: `frontend`
   - **Root Directory**: `frontend`
4. Push your changes to GitHub to trigger the final deployment.

---

## 🛠️ Local Development

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
python -m http.server 3000
```
