# 🇳🇬 NairaHR Agent

> An AI-powered HR assistant built for Nigerian SMEs — handling recruitment, onboarding, and employee support with local compliance built in.

[![Hugging Face Spaces](https://img.shields.io/badge/🤗%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-green)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## What It Does

NairaHR is an agentic HR assistant that helps Nigerian HR teams:

| Module | What it handles |
|---|---|
| **CV Parser** | Accepts PDF or text CVs, extracts skills, education, and experience |
| **Job Matcher** | Scores candidates against job descriptions using embeddings |
| **Policy Q&A** | Answers employee questions from a Nigerian-compliant knowledge base |
| **Onboarding Generator** | Builds a personalised onboarding task checklist for new hires |

---

## System Architecture

```
User Input (CV / Job Role / Query)
         │
         ▼
┌─────────────────────┐
│   Agent Brain        │  ← Qwen2.5-7B-Instruct (via HF Inference API)
│   (Orchestrator)     │
└────────┬────────────┘
         │         ┌─────────────────────────┐
         │─────────▶  Knowledge Base (RAG)   │ ← Policies, JDs, Templates
         │         └─────────────────────────┘
    ┌────┴──────────────────────────────────┐
    │                                        │
    ▼            ▼              ▼            ▼
CV Parser   Job Matcher    Policy Q&A   Onboarding
(PyMuPDF/   (all-MiniLM   (ChromaDB    (LLM template
 Tesseract)  -L6-v2)       + LLM)       generation)
    │            │              │            │
    └────────────┴──────────────┴────────────┘
                          │
                          ▼
                  HR Dashboard (Gradio UI)
```

---

## Model Stack

| Role | Model | Why |
|---|---|---|
| Agent LLM | `Qwen/Qwen2.5-7B-Instruct` | Best multilingual open model for agents; Apache 2.0; strong instruction following |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` | Fast, free, excellent semantic similarity for CV↔JD matching |
| OCR | `pytesseract` + `PyMuPDF` | PDF text extraction; Tesseract for scanned documents |
| Vector DB | `ChromaDB` | Lightweight, runs in-process, no external service needed for hackathon |
| UI | `Gradio` | Free HF Spaces deployment, shareable URL instantly |

---

## Quickstart

```bash
# Clone the repo
git clone https://github.com/YOUR_ORG/nairahr-agent.git
cd nairahr-agent

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Add your HF_TOKEN to .env

# Run locally
python app.py
```

---

## Project Structure

```
nairahr/
├── app.py                    # Gradio UI entry point (HF Spaces compatible)
├── requirements.txt
├── .env.example
├── README.md
│
├── src/
│   ├── agent/
│   │   └── orchestrator.py   # Main agent loop & tool routing
│   ├── matching/
│   │   └── matcher.py        # CV↔JD embedding + scoring
│   ├── ocr/
│   │   └── parser.py         # PDF/image CV extraction
│   ├── onboarding/
│   │   └── generator.py      # Onboarding checklist generator
│   └── policy_qa/
│       └── qa_engine.py      # RAG pipeline for policy Q&A
│
├── knowledge_base/
│   ├── nigerian_labour_act.md
│   ├── hr_policies_template.md
│   ├── onboarding_templates.md
│   ├── job_descriptions/
│   │   ├── software_engineer.md
│   │   ├── product_manager.md
│   │   └── sales_executive.md
│   └── compliance/
│       ├── nsitf_guide.md
│       ├── pencom_guide.md
│       └── ndpa_summary.md
│
├── docs/
│   ├── ARCHITECTURE.md       # This document (detailed)
│   ├── MODEL_RESEARCH.md     # Model selection rationale
│   ├── DEPLOYMENT.md         # Deployment guide
│   └── KNOWLEDGE_BASE.md     # How to extend the KB
│
├── tests/
│   ├── test_matcher.py
│   ├── test_parser.py
│   └── test_qa.py
│
└── assets/
    └── demo_cv.pdf           # Sample CV for demo
```

---

## Deployment

**Hugging Face Spaces (Recommended — free)**
```bash
# Push to your HF Space repo
git remote add space https://huggingface.co/spaces/YOUR_USERNAME/nairahr
git push space main
```

**Local with Docker**
```bash
docker build -t nairahr .
docker run -p 7860:7860 nairahr
```

---

## Nigerian Compliance Coverage

- ✅ Nigerian Labour Act (Cap L1, LFN 2004)
- ✅ Pension Reform Act 2014 (PENCOM — 10% employer / 8% employee)
- ✅ NSITF — 1% payroll contribution
- ✅ Nigeria Data Protection Act 2023 (NDPA)
- ✅ National Minimum Wage Act 2024 (₦70,000/month)
- ✅ Employee Compensation Act
- ✅ ITF (Industrial Training Fund)
- ✅ 12-week maternity leave provision

---

## Inspired By / Prior Art

| Project | What it does | Link |
|---|---|---|
| autonomous-hr-chatbot | LangChain HR agent with employee data + policy Q&A | [GitHub](https://github.com/stepanogil/autonomous-hr-chatbot) |
| Resume-Screening-RAG-Pipeline | RAG-based CV↔JD matching with sub-query decomposition | [GitHub](https://github.com/Hungreeee/Resume-Screening-RAG-Pipeline) |
| AskJohnny (GBS SA) | Labour law chatbot for South Africa (closest African analogue) | [Link](https://www.globalbusiness.co.za/ai-bots-for-hr-labour-law-and-business-automation) |
| RAGFlow | Production-grade RAG engine with agent support | [GitHub](https://github.com/infiniflow/ragflow) |

NairaHR differs by targeting Nigerian-specific compliance, SME affordability, and hackathon-ready demo scope.

---

## Team

Built for the Hugging Face / AI Hackathon — Nigeria track.

---

## License

MIT
