# NairaHR — Model Research & Selection

## Research Summary

This document records the model research done for NairaHR, with reasoning for each selection.

---

## 1. Agent LLM (Reasoning & Conversation)

### Requirements
- Instruction following (multi-step agent tasks)
- Multilingual (Nigerian English, potential Yoruba/Igbo/Hausa)
- Free/open for hackathon use
- Deployable via HF Inference API (no GPU required for demo)

### Candidates Evaluated

| Model | Params | License | Multilingual | Agent capability | HF Inference API | Verdict |
|---|---|---|---|---|---|---|
| `Qwen2.5-7B-Instruct` | 7B | Apache 2.0 | ✅ 29 langs | ✅ Strong | ✅ Free tier | **Selected** |
| `Meta-Llama-3.1-8B-Instruct` | 8B | Llama Community | ⚠️ Limited | ✅ Strong | ✅ Free tier | Runner-up |
| `mistralai/Mistral-7B-Instruct-v0.3` | 7B | Apache 2.0 | ⚠️ Limited | ✅ Good | ✅ Free tier | Good fallback |
| `google/gemma-2-9b-it` | 9B | Gemma (permissive) | ⚠️ Limited | ✅ Good | ✅ Free tier | Option |
| `Qwen3-8B` | 8B | Apache 2.0 | ✅ 200+ langs | ✅ Excellent | ✅ Free tier | Future upgrade |

### Decision: `Qwen/Qwen2.5-7B-Instruct`

**Why:**
- Apache 2.0 license — clean for commercial and hackathon use
- Strong multilingual capability — 29 languages including African English variants
- Excellent instruction following benchmarks (MMLU, MT-Bench)
- Runs on HF Inference API serverless endpoint (no GPU provisioning needed for demo)
- 128K context window — handles long CVs and policy documents without chunking issues
- Active community, quantized GGUF versions available for local fallback

**HF link:** https://huggingface.co/Qwen/Qwen2.5-7B-Instruct

**API call:**
```python
from huggingface_hub import InferenceClient

client = InferenceClient("Qwen/Qwen2.5-7B-Instruct", token=HF_TOKEN)
response = client.text_generation(prompt, max_new_tokens=512)
```

**Future upgrade path:** `Qwen3-8B` (Apache 2.0, 200+ languages including Yoruba/Igbo/Hausa, hybrid thinking mode) — upgrade when stable on HF serverless.

---

## 2. Embedding Model (CV ↔ Job Description Matching)

### Requirements
- Semantic similarity (not keyword matching)
- Fast inference (real-time scoring in demo)
- Free, no API key needed
- Handles HR-domain text well

### Candidates Evaluated

| Model | Dims | Speed | HR domain | Free | Verdict |
|---|---|---|---|---|---|
| `all-MiniLM-L6-v2` | 384 | ⚡ Very fast | ✅ Good | ✅ | **Selected** |
| `all-mpnet-base-v2` | 768 | 🔄 Medium | ✅ Better | ✅ | Good alternative |
| `BAAI/bge-small-en-v1.5` | 384 | ⚡ Very fast | ✅ Good | ✅ | Alternative |
| `intfloat/e5-small-v2` | 384 | ⚡ Fast | ✅ Good | ✅ | Alternative |
| OpenAI `text-embedding-3-small` | 1536 | 🔄 API call | ✅ Excellent | ❌ Paid | Not for hackathon |

### Decision: `sentence-transformers/all-MiniLM-L6-v2`

**Why:**
- 80MB download — fits in HF Spaces free CPU instance
- 14,200+ downloads/day — most battle-tested sentence transformer
- 384-dimension vectors — fast cosine similarity computation
- Strong on short-to-medium text (perfect for CV sections and JDs)
- Runs fully local — no API key, no latency, no cost

**HF link:** https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2

**Usage:**
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
cv_embedding = model.encode(cv_text)
jd_embedding = model.encode(job_description)
score = cosine_similarity([cv_embedding], [jd_embedding])[0][0]
```

---

## 3. OCR / Document Parsing

### Requirements
- Extract text from uploaded PDF CVs
- Handle both digital PDFs (text layer) and scanned images
- Python library (no API call)

### Decision: `PyMuPDF` (primary) + `pytesseract` (fallback)

| Library | Handles | Speed | Notes |
|---|---|---|---|
| `PyMuPDF (fitz)` | Digital PDFs | ⚡ Very fast | First choice; extracts text layer directly |
| `pytesseract` | Scanned images | 🔄 Slower | Fallback for image-only PDFs |
| `pdfplumber` | Tables in PDFs | 🔄 Medium | Alternative for structured CVs |

**Why this combination:**
- Most Nigerian CVs submitted digitally → PyMuPDF handles 90% of cases
- Scanned certificates and paper CVs → Tesseract covers the rest
- No cloud API needed — runs entirely local

```python
import fitz  # PyMuPDF

def extract_pdf_text(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    if len(text.strip()) < 100:
        # Fall back to OCR
        text = ocr_fallback(pdf_bytes)
    return text
```

---

## 4. Vector Database (Knowledge Base)

### Requirements
- Store and retrieve policy document chunks
- Fast similarity search
- No external server (hackathon simplicity)
- Free

### Decision: `ChromaDB` (in-process)

| Option | Hosting | Setup | Performance | Verdict |
|---|---|---|---|---|
| `ChromaDB` | In-process | 1 line | ✅ Sufficient | **Selected** |
| `FAISS` | In-process | 5 lines | ✅ Faster | Good alternative |
| `Pinecone` | Cloud | Account needed | ✅ Production-grade | Post-hackathon |
| `Weaviate` | Cloud/Self-hosted | Docker | ✅ Production-grade | Post-hackathon |
| `Qdrant` | Cloud/Self-hosted | Docker | ✅ Production-grade | Post-hackathon |

**Why ChromaDB for hackathon:**
- `pip install chromadb` — single dependency
- Persists to disk — knowledge base survives restarts
- Built-in embedding support — can use our MiniLM model directly
- Easy to migrate to Pinecone/Qdrant post-hackathon

---

## 5. Optional: Nigerian Language Support

### Current Status
- Nigerian-accented English is handled well by Qwen2.5 without special tuning
- Full Yoruba/Igbo/Hausa support: out of scope for hackathon

### Future Options

| Model | Languages | Status |
|---|---|---|
| YorubaLlama | Yoruba | Research-stage; see https://huggingface.co/Lagos-NLP |
| NigerianAccentedEnglish | Nigerian English ASR | Available on HF; for voice input |
| Qwen3-8B | 200+ langs (includes Hausa) | Stable for text; best near-term path |
| AfroLLM | Multiple African languages | Research-stage |

**Recommendation:** For the hackathon, add a UI note "Yoruba/Igbo support coming soon" and use Qwen2.5's multilingual base. Upgrade to Qwen3 for language expansion post-launch.

---

## Model Stack Summary

```
┌─────────────────────────────────────────────────────┐
│  NairaHR Model Stack                                │
│                                                     │
│  Agent LLM:    Qwen2.5-7B-Instruct (HF Inference)  │
│  Embeddings:   all-MiniLM-L6-v2   (local)          │
│  OCR:          PyMuPDF + Tesseract (local)          │
│  Vector DB:    ChromaDB            (in-process)     │
│  UI:           Gradio              (HF Spaces)      │
│                                                     │
│  Total API cost for demo: ~$0 (HF free tier)       │
│  Total local compute: CPU-only (no GPU needed)     │
└─────────────────────────────────────────────────────┘
```
