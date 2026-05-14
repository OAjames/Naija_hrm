# NairaHR — System Architecture

## Overview

NairaHR is an agentic AI system. It is not a simple chatbot — it is an orchestrator that routes user inputs to specialised tools and synthesises results into actionable HR outputs.

---

## Layer 1: User Interface (Gradio)

**File:** `app.py`

The UI presents four tabs:

| Tab | Input | Output |
|---|---|---|
| CV Screening | PDF upload + job role selector | Match score, strengths, gaps, recommendation |
| Policy Q&A | Free-text employee question | Policy answer with source citation + escalation flag |
| Onboarding | Candidate name + role | Personalised onboarding checklist (PDF export) |
| HR Dashboard | (auto-populated) | Candidate shortlist, recurring questions, workflow status |

Gradio is deployed on Hugging Face Spaces. Entry point must be `app.py` at repo root.

---

## Layer 2: Agent Brain (Orchestrator)

**File:** `src/agent/orchestrator.py`

The agent brain uses **Qwen2.5-7B-Instruct** via the Hugging Face Inference API. It:

1. Classifies the user intent (recruitment / policy / onboarding)
2. Routes to the correct tool
3. Passes tool outputs back to the LLM for a final natural-language summary
4. Flags escalations (sensitive queries, low-confidence answers)

The orchestrator is built as a simple ReAct-style loop (no heavy framework needed for hackathon scope):

```python
# Pseudo-code
def run_agent(user_input, context):
    intent = classify_intent(user_input)          # LLM call 1
    if intent == "recruitment":
        raw = matcher.score(cv, job_description)
    elif intent == "policy":
        raw = qa_engine.answer(user_input)
    elif intent == "onboarding":
        raw = generator.create_checklist(role)
    response = llm.synthesise(raw, user_input)    # LLM call 2
    return response
```

---

## Layer 3: Tool Modules

### 3a. CV Parser (`src/ocr/parser.py`)

**Libraries:** `PyMuPDF (fitz)`, `pytesseract`, `Pillow`

**Flow:**
1. Accept PDF upload from Gradio
2. Try text extraction with PyMuPDF (fast, handles digital PDFs)
3. If text yield < 100 characters, fall back to Tesseract OCR (handles scanned documents)
4. Output: structured dict `{name, email, phone, skills[], experience[], education[]}`

**Note:** Nigerian CVs often include: NYSC status, state of origin, and referee contacts. Parser is tuned to extract these fields.

### 3b. Job Matcher (`src/matching/matcher.py`)

**Model:** `sentence-transformers/all-MiniLM-L6-v2`

**Flow:**
1. Encode CV text and job description text into embedding vectors
2. Compute cosine similarity score (0–1)
3. Section-level scoring: skills (40%), experience (35%), education (25%)
4. Output: `{overall_score, skills_score, experience_score, gaps[], strengths[], recommendation}`

**Nigerian context:** Job descriptions include local role norms (e.g., NYSC completion requirement for junior roles, state-specific preferences for field roles).

### 3c. Policy Q&A (`src/policy_qa/qa_engine.py`)

**Stack:** `ChromaDB` (vector store) + `Qwen2.5-7B-Instruct` (generation)

**Flow:**
1. Load knowledge base markdown files into ChromaDB at startup
2. On query: embed the question, retrieve top-3 most relevant chunks
3. Feed chunks + question to LLM for a grounded answer
4. Add source citation (e.g., "Nigerian Labour Act, Section 18")
5. Escalation logic: if confidence < threshold OR query contains sensitive keywords (termination, discrimination, harassment), flag for human HR review

**Knowledge base topics:**
- Leave entitlements (annual, maternity, sick)
- Minimum wage (₦70,000 as of 2024)
- Pension deductions (PENCOM)
- NSITF contributions
- Termination and notice periods
- NYSC policy for hiring fresh graduates

### 3d. Onboarding Generator (`src/onboarding/generator.py`)

**Model:** `Qwen2.5-7B-Instruct`

**Flow:**
1. Accept: new hire name, role, department, start date
2. LLM generates a structured checklist using a template prompt
3. Output: markdown checklist with sections:
   - **Pre-arrival** (email setup, access cards, desk)
   - **Day 1** (ID documentation, welcome meeting, system access)
   - **Week 1** (policy reading, team introductions, role briefing)
   - **Month 1** (performance targets, probation review scheduling)
   - **Compliance** (NSITF registration, pension enrolment, PAYE setup)

---

## Layer 4: Knowledge Base

**Format:** Markdown files in `/knowledge_base/`

**Loaded at startup** into ChromaDB using chunk-based ingestion (500 tokens/chunk, 50 token overlap).

**Files:**

| File | Content |
|---|---|
| `nigerian_labour_act.md` | Key provisions of the Labour Act (Cap L1) |
| `hr_policies_template.md` | Generic SME HR policy covering leave, conduct, grievance |
| `onboarding_templates.md` | Role-specific onboarding checklists |
| `compliance/nsitf_guide.md` | NSITF registration and contribution guide |
| `compliance/pencom_guide.md` | Pension contribution rules and enrolment |
| `compliance/ndpa_summary.md` | Data protection obligations for HR data |

---

## Data Flow Diagram

```
┌──────────────────────────────────────────────────┐
│                  Gradio UI (app.py)               │
└──────────┬───────────────────────────────────────┘
           │ user input (text / PDF)
           ▼
┌──────────────────────────────────────────────────┐
│            Orchestrator (orchestrator.py)         │
│  - Intent classification (LLM)                   │
│  - Tool routing                                  │
│  - Final synthesis (LLM)                         │
└───┬──────────────┬──────────────┬────────────────┘
    │              │              │
    ▼              ▼              ▼
┌───────┐    ┌──────────┐   ┌──────────────┐
│  OCR  │    │ Matcher  │   │  Policy QA   │
│Parser │    │(MiniLM   │   │ (Chroma RAG  │
│       │    │ embed)   │   │  + LLM)      │
└───┬───┘    └────┬─────┘   └──────┬───────┘
    │             │                │
    └─────────────┴────────────────┘
                  │
                  ▼
         ┌────────────────┐
         │  Onboarding    │
         │  Generator     │
         │  (LLM template)│
         └────────────────┘
                  │
                  ▼
         ┌────────────────┐
         │  HR Dashboard  │
         │  (Gradio tabs) │
         └────────────────┘
```

---

## Escalation Logic

The agent never guesses on sensitive topics. Escalation triggers:

- Query mentions: termination, dismissal, discrimination, harassment, pregnancy
- Confidence score < 0.6 from retrieval
- Query is about a specific named employee (privacy risk)
- Query involves salary negotiation or legal dispute

On escalation: the agent responds with a partial answer + "This requires review by a qualified HR officer" and logs the query to the dashboard.

---

## Nigerian-Specific Design Decisions

| Design choice | Rationale |
|---|---|
| Qwen2.5 as base LLM | Best multilingual open model; handles Nigerian-accented English input well |
| NYSC field in CV parser | NYSC completion is a standard hiring requirement for Nigerian firms |
| ₦70,000 minimum wage in KB | Updated 2024 minimum wage hardcoded into policy KB |
| NSITF + PENCOM compliance modules | Most Nigerian SMEs lack HR systems; this fills the gap |
| Escalation on tribe/religion signals | Nigerian HR sensitivity; agent avoids discriminatory outputs |
| Pidgin English fallback (future) | Planned: detect Pidgin input and respond in Pidgin for accessibility |
