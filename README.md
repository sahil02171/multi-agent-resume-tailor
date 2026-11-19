#  Multi-Agent Research & Resume Tailoring Studio

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-1C3C3C?style=for-the-badge)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-Structured%20AI-4285F4?style=for-the-badge&logo=google&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Responsive%20UI-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)

An end-to-end **Agentic AI application** built with **LangGraph**, **Google Gemini**, and **Tavily Web Search** that analyzes target job descriptions, researches company tech stacks in real time, calculates ATS skill gaps, and generates factually grounded, ATS-optimized resumes and cover letters.

---

##  Key Engineering Highlights

* **  Parallel Multi-Agent Execution:** Executes JD parsing and Resume-to-JD Gap Analysis concurrently via `ThreadPoolExecutor` inside a compiled LangGraph state workflow, cutting end-to-end latency by ~50%.
* **  Self-Healing Multi-LLM Failover:** Implements automatic retry and seamless failover across active Google Gemini models (`gemini-3.5-flash-lite`, `gemini-3.8-flash`) with an optional **Groq (`llama-3.3-70b-versatile`)** fallback to prevent `503` overload or `429` rate-limit failures.
* **  Live Company Intelligence & Caching:** Integrates **Tavily Search API** with in-memory caching to fetch real-time company engineering culture and tech stack insights without redundant API calls.
* **  Strict Anti-Hallucination Guardrails:** Uses **Pydantic v2** strict JSON schemas (`response_schema`) and prompt-level verification rules to ensure zero fabricated skills, degrees, or job titles.
* **  Instant ATS PDF Generation:** Exports a clean, single-column, ATS-parsable PDF resume using `fpdf2` alongside a tailored cover letter.
* **  Mobile-First Responsive UI:** Custom SaaS dark-mode interface with glassmorphic KPI cards, skill badges, and collapsible inputs designed for seamless use across phones, tablets, and laptops.

---

##   System Architecture

```text
[User PDF Resume + Target JD / URL]
               │
               ▼
   ┌───────────────────────┐
   │   PyMuPDF / Scraper   │  ──► Extracts clean resume & JD text
   └───────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────┐
│           LangGraph Parallel Multi-Agent Workflow        │
│                                                          │
│  ┌─────────────────────┐      ┌───────────────────────┐  │
│  │ Agent 1: Researcher │      │ Agent 2: Gap Analyzer │  │
│  │ (JD + Tavily Intel) │      │ (ATS Score & Missing) │  │
│  └──────────┬──────────┘      └───────────┬───────────┘  │
│             └──────────────┬──────────────┘              │
│                            ▼                             │
│            ┌───────────────────────────────┐             │
│            │ Agent 3 & 4: Writer & Critic  │             │
│            │ (Grounded Bullets & Letter)   │             │
│            └───────────────┬───────────────┘             │
└────────────────────────────┼─────────────────────────────┘
                             ▼
     [ATS Score Dashboard + Downloadable Tailored PDF]