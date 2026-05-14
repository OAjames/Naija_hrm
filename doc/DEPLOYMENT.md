# NairaHR — Deployment Guide

## Option 1: Hugging Face Spaces (Recommended for Hackathon)

**Why:** Free, always online, shareable URL, no infrastructure management.

### Steps

**1. Create your HF Space**
- Go to https://huggingface.co/new-space
- Name: `nairahr-agent`
- SDK: `Gradio`
- Hardware: `CPU basic` (free — 2 vCPU, 16GB RAM)
- Visibility: `Public`

**2. Clone and push**
```bash
# Clone your new space
git clone https://huggingface.co/spaces/YOUR_USERNAME/nairahr-agent
cd nairahr-agent

# Copy project files in
cp -r /path/to/nairahr/* .

# Push
git add .
git commit -m "Initial NairaHR deployment"
git push
```

**3. Add secrets**
In your Space settings → Variables and Secrets:
```
HF_TOKEN = your_huggingface_token
```

**4. Verify**
- Space builds automatically (2–5 minutes)
- Visit: `https://huggingface.co/spaces/YOUR_USERNAME/nairahr-agent`

### File Requirements for HF Spaces
- Entry point MUST be `app.py` at repo root
- `requirements.txt` must list all dependencies
- Secrets go in Space settings, never in code

---

## Option 2: Local Development

```bash
# Prerequisites: Python 3.10+
git clone https://github.com/YOUR_ORG/nairahr-agent.git
cd nairahr-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your HF_TOKEN

# Run
python app.py
# Open http://localhost:7860
```

---

## Option 3: Docker

```dockerfile
# Dockerfile (included in repo)
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install Tesseract for OCR fallback
RUN apt-get update && apt-get install -y tesseract-ocr

COPY . .
EXPOSE 7860

CMD ["python", "app.py"]
```

```bash
docker build -t nairahr .
docker run -p 7860:7860 -e HF_TOKEN=your_token nairahr
```

---

## requirements.txt

```
gradio>=4.0.0
huggingface-hub>=0.20.0
sentence-transformers>=2.7.0
chromadb>=0.4.0
PyMuPDF>=1.24.0
pytesseract>=0.3.10
Pillow>=10.0.0
python-dotenv>=1.0.0
requests>=2.31.0
langchain-community>=0.0.20
```

---

## Environment Variables

```bash
# .env.example
HF_TOKEN=hf_your_token_here              # Required: HF Inference API access
CHROMA_PERSIST_DIR=./chroma_db           # Where ChromaDB stores its index
LOG_LEVEL=INFO
ESCALATION_THRESHOLD=0.6                 # RAG confidence below this → human flag
```

---

## Performance Notes (HF Spaces Free CPU)

| Operation | Expected latency | Notes |
|---|---|---|
| CV text extraction | <1s | PyMuPDF is very fast |
| Embedding computation | 1–2s | MiniLM runs on CPU fine |
| LLM inference | 5–15s | HF Inference API serverless; cold start adds ~5s |
| RAG retrieval | <1s | ChromaDB in-process |
| Full pipeline | 10–20s | Acceptable for demo |

**Tip:** Pre-warm the LLM by sending a dummy request at startup. Add a loading spinner in the Gradio UI so judges see progress, not a frozen screen.

---

## Post-Hackathon Scaling

| Need | Solution |
|---|---|
| Faster LLM | HF Spaces GPU upgrade ($9/hr) or vLLM on cloud |
| Production vector DB | Migrate ChromaDB → Pinecone or Qdrant |
| Persistent HR data | Add PostgreSQL for candidate records |
| WhatsApp integration | Twilio + Gradio API endpoint |
| Nigerian language support | Add Qwen3 or fine-tuned Yoruba model |
