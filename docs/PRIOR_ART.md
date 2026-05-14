# NairaHR — Prior Art & Research

## Has This Been Done Before?

**Short answer:** Partially — but not for Nigeria, not as an integrated agent, and not for SMEs.

---

## What Exists Globally

### 1. Autonomous HR Chatbot (stepanogil)
**GitHub:** https://github.com/stepanogil/autonomous-hr-chatbot  
**What it does:** LangChain-based HR agent that answers employee queries using employee CSV data and a policy document. Uses OpenAI + Pinecone + Streamlit.  
**Similarity to NairaHR:** Policy Q&A, employee data lookup.  
**Gap:** No CV screening, no onboarding, no African/Nigerian compliance, requires paid OpenAI API.

### 2. Resume Screening RAG Pipeline (Hungreeee)
**GitHub:** https://github.com/Hungreeee/Resume-Screening-RAG-Pipeline  
**What it does:** RAG-based CV screening system. LLM agent generates sub-queries, retrieves matching resumes, re-ranks them against a job description.  
**Similarity to NairaHR:** Core matching logic is very close to our job matcher module.  
**Gap:** No HR policy Q&A, no onboarding, no Nigerian context, research/thesis project.

### 3. AI-Powered ATS with Milvus + Spring Boot
**GitHub:** https://github.com/topics/ai-recruitment (multiple repos)  
**What it does:** Full ATS with resume parsing, RAG semantic search, recruitment funnel analytics.  
**Similarity to NairaHR:** Recruitment pipeline.  
**Gap:** Enterprise Java stack, no Nigerian localisation.

### 4. AskJohnny (GBS SA)
**Link:** https://www.globalbusiness.co.za/ai-bots-for-hr-labour-law-and-business-automation  
**What it does:** South African labour law chatbot. Answers HR policy questions, helps with disciplinary enquiries, workforce forecasting. Available on WhatsApp.  
**Similarity to NairaHR:** The closest African analogue — policy Q&A for African labour law.  
**Gap:** South African law only, not open source, no CV screening or onboarding, proprietary.

### 5. Paradox.ai — Olivia
**Link:** https://www.paradox.ai  
**What it does:** Enterprise recruitment chatbot. Screens candidates, schedules interviews, handles onboarding steps. Used by Walmart, McDonald's, others.  
**Similarity to NairaHR:** Full recruitment + onboarding loop.  
**Gap:** Closed-source, expensive enterprise pricing, built for US/EU markets, no Nigerian compliance.

### 6. LinkedIn Hiring Assistant (2024)
**Link:** https://techcrunch.com (LinkedIn AI Hiring Assistant launch)  
**What it does:** AI agent that drafts JDs, sources candidates, initiates outreach. Built on GPT technology.  
**Similarity to NairaHR:** Recruitment automation.  
**Gap:** Not open source, no African market focus, candidate response times fell 7 days → 24 hours with AI.

### 7. RAGFlow (infiniflow)
**GitHub:** https://github.com/infiniflow/ragflow  
**What it does:** Production-grade RAG engine with agent support. Document understanding, multi-LLM support, visual pipeline builder.  
**Similarity to NairaHR:** The RAG infrastructure our policy Q&A is based on.  
**Gap:** General-purpose, not HR-specific, heavy infrastructure (Docker + Elasticsearch).

---

## What Is Unique About NairaHR

| Feature | NairaHR | Everything else |
|---|---|---|
| Nigerian Labour Act knowledge base | ✅ Built-in | ❌ None |
| PENCOM / NSITF compliance | ✅ Built-in | ❌ None |
| NYSC field in CV parser | ✅ Yes | ❌ Not applicable |
| ₦70,000 minimum wage (2024) | ✅ Yes | ❌ None |
| Nigerian SME cost profile | ✅ Free to run | ❌ Paid enterprise |
| Integrated: CV + Matching + Policy + Onboarding | ✅ One agent | ❌ Separate tools |
| Deployable free on HF Spaces | ✅ Yes | ❌ Most require cloud spend |
| Nigerian-accented English support (roadmap) | ✅ Planned | ❌ None |
| Pidgin English support (roadmap) | ✅ Planned | ❌ None |

---

## Key Papers and Resources

| Resource | Relevance |
|---|---|
| "Reimagining recruitment: traditional methods meet AI interventions (2003–2023)" — Taylor & Francis | 20-year survey of AI in recruitment |
| "AI in Recruitment 2025: Year in Review" — HeroHunt | Industry overview; Paradox, LinkedIn, HireVue case studies |
| "Top 10 AI Tools Every HR Professional in Nigeria Should Know in 2025" — NuCamp | Nigerian HR tech landscape |
| YorubaLlama — Lagos NLP | Nigerian language model foundation; https://huggingface.co/Lagos-NLP |
| NigerianAccentedEnglish — HF | ASR for Nigerian-accented speech; https://huggingface.co |
| Qwen2.5 technical report — Alibaba | Multilingual LLM we selected |
| Nigerian Employment & Labour Laws Report 2026 — ICLG | Primary source for compliance KB |

---

## Conclusion

NairaHR is not starting from a blank page — the components (RAG, CV matching, HR chatbots) exist separately. What does not exist is:

1. An **integrated agentic system** handling the full loop (CV → match → onboarding → employee support).
2. Built **for Nigeria** — with local compliance, local salary benchmarks, and local HR sensitivities.
3. **Free to run** for SMEs — no enterprise contracts, no GPU required.

That gap is what NairaHR fills.
