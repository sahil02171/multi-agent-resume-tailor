import time
import streamlit as st
from tools import extract_text_from_pdf, scrape_job_url
from agents import resume_agent_app
from pdf_generator import generate_tailored_pdf

st.set_page_config(
    page_title="ResumeAI Studio | Multi-Agent ATS Tailor",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- Premium Career SaaS CSS (Mobile + Desktop Optimized) ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* Fix top header overlap on Mobile & Desktop */
    header[data-testid="stHeader"] {
        background: rgba(11, 15, 25, 0.75) !important;
        backdrop-filter: blur(10px);
    }
    .block-container {
        padding-top: 3.6rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 1120px !important;
    }

    /* Premium Resume Studio Hero Card */
    .hero-wrapper {
        background: radial-gradient(circle at top right, rgba(99, 102, 241, 0.25), transparent 55%),
                    linear-gradient(135deg, #111827 0%, #1E1B4B 60%, #0F172A 100%);
        border: 1px solid rgba(129, 140, 248, 0.3);
        border-radius: 20px;
        padding: 1.75rem 2rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 20px 35px -15px rgba(0, 0, 0, 0.6);
        position: relative;
        overflow: hidden;
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(99, 102, 241, 0.18);
        border: 1px solid rgba(129, 140, 248, 0.45);
        color: #A5B4FC;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 5px 12px;
        border-radius: 999px;
        margin-bottom: 0.75rem;
    }
    .hero-title {
        font-size: 1.9rem;
        font-weight: 800;
        color: #FFFFFF;
        margin: 0 0 0.45rem 0;
        line-height: 1.2;
        letter-spacing: -0.02em;
    }
    .hero-title span {
        background: linear-gradient(90deg, #818CF8, #38BDF8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
        font-size: 0.95rem;
        color: #CBD5E1;
        margin: 0 0 1.15rem 0;
        line-height: 1.5;
    }

    /* 3-Step Visual Resume Pipeline Strip */
    .pipeline-strip {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        padding-top: 0.9rem;
        border-top: 1px solid rgba(148, 163, 184, 0.15);
    }
    .step-pill {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(148, 163, 184, 0.2);
        color: #E2E8F0;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 6px 12px;
        border-radius: 10px;
    }
    .step-pill b {
        color: #818CF8;
    }

    /* Responsive 2x2 / 4-Col KPI Grid */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin: 0.75rem 0 1rem 0;
    }
    .kpi-card {
        background: linear-gradient(180deg, #161F33 0%, #111827 100%);
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-radius: 14px;
        padding: 0.95rem 1.1rem;
        transition: all 0.2s ease;
    }
    .kpi-card:hover {
        border-color: rgba(129, 140, 248, 0.55);
        transform: translateY(-2px);
    }
    .kpi-label {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #94A3B8;
        margin-bottom: 0.3rem;
    }
    .kpi-value {
        font-size: 1.15rem;
        font-weight: 700;
        color: #F8FAFC;
        line-height: 1.3;
        word-break: break-word;
    }

    /* Resume Sheet & Bullet Cards */
    .resume-sheet-card {
        background: #131A2A;
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-left: 4px solid #6366F1;
        border-radius: 14px;
        padding: 1.25rem 1.4rem;
        margin-bottom: 1rem;
    }
    .bullet-card {
        background: rgba(30, 41, 59, 0.55);
        border: 1px solid rgba(148, 163, 184, 0.14);
        border-radius: 10px;
        padding: 0.75rem 0.95rem;
        margin-bottom: 0.6rem;
        color: #E2E8F0;
        font-size: 0.92rem;
        line-height: 1.55;
    }

    /* Skill Badges */
    .skill-badge-match {
        display: inline-block;
        background: rgba(16, 185, 129, 0.14);
        border: 1px solid rgba(16, 185, 129, 0.4);
        color: #6EE7B7;
        padding: 5px 12px;
        border-radius: 999px;
        margin: 4px 5px 4px 0;
        font-size: 0.82rem;
        font-weight: 600;
    }
    .skill-badge-miss {
        display: inline-block;
        background: rgba(244, 63, 94, 0.14);
        border: 1px solid rgba(244, 63, 94, 0.4);
        color: #FDA4AF;
        padding: 5px 12px;
        border-radius: 999px;
        margin: 4px 5px 4px 0;
        font-size: 0.82rem;
        font-weight: 600;
    }

    /* Primary CTA Button Polish */
    .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #4F46E5 0%, #6366F1 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.65rem 1.25rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.01em;
        box-shadow: 0 8px 20px -6px rgba(99, 102, 241, 0.65);
    }

    /* Mobile & Tablet Responsive Adjustments */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 3.4rem !important;
            padding-left: 0.85rem !important;
            padding-right: 0.85rem !important;
        }
        .hero-wrapper {
            padding: 1.25rem 1.15rem;
            border-radius: 16px;
        }
        .hero-title {
            font-size: 1.4rem;
        }
        .hero-subtitle {
            font-size: 0.84rem;
        }
        .step-pill {
            font-size: 0.74rem;
            padding: 5px 9px;
        }
        /* Compact 2x2 grid on phones instead of 4 tall stacked cards */
        .kpi-grid {
            grid-template-columns: repeat(2, 1fr);
            gap: 9px;
        }
        .kpi-card {
            padding: 0.8rem 0.9rem;
        }
        .kpi-value {
            font-size: 1rem;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            overflow-x: auto;
            flex-wrap: nowrap;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 0.8rem;
            padding: 8px 10px;
            white-space: nowrap;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

SAMPLE_JD = """Role: Junior Data Analyst / AI Engineer
Company: Swiggy
Location: Bengaluru, India

Responsibilities:
- Build automated ETL pipelines and interactive BI dashboards using Python, SQL, and Power BI.
- Analyze user order trends, delivery latency, and retention cohorts using Pandas, NumPy, and Scikit-learn.
- Develop LLM-powered internal analytics assistants and predictive demand forecasting models.

Requirements:
- Strong proficiency in Python, SQL, Power BI (DAX, Power Query), and Machine Learning fundamentals.
- Hands-on experience building end-to-end data analytics dashboards or predictive ML projects.
- Familiarity with Generative AI, prompt engineering, and API integration is a strong plus."""

# --- Premium Resume Studio Hero Section ---
st.markdown(
    """
    <div class="hero-wrapper">
        <div class="hero-badge">📄 AI-POWERED ATS RESUME & CAREER STUDIO</div>
        <div class="hero-title">Tailor Your Resume for Any Role in <span>Seconds</span></div>
        <div class="hero-subtitle">
            Upload your base PDF resume & target job description. Our parallel LangGraph AI agents benchmark ATS keywords,
            research company tech stacks, and craft a recruiter-ready resume & cover letter.
        </div>
        <div class="pipeline-strip">
            <div class="step-pill"><b>01</b> Upload Base PDF</div>
            <div class="step-pill"><b>02</b> ATS Gap & Company Intel</div>
            <div class="step-pill"><b>03</b> Export Tailored Resume</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Step 1: Upload & Job Details ---
has_result = "result" in st.session_state
with st.expander("📤 Upload Resume & Target Job Description", expanded=not has_result):
    col_left, col_right = st.columns([1, 1.3], gap="large")

    with col_left:
        candidate_name = st.text_input("👤 Candidate Full Name", value="Sahil Raj")
        uploaded_pdf = st.file_uploader("📄 Base Resume (PDF Format)", type=["pdf"])
        jd_url = st.text_input("🔗 Job Posting Link (Optional)", placeholder="https://careers.company.com/job/...")

    with col_right:
        top_row1, top_row2 = st.columns([1.3, 1])
        with top_row1:
            st.markdown("**📝 Target Job Description**")
        with top_row2:
            if st.button("⚡ Try Sample JD", use_container_width=True):
                st.session_state["sample_jd"] = SAMPLE_JD

        jd_manual_text = st.text_area(
            "Job Description",
            value=st.session_state.get("sample_jd", ""),
            height=175,
            label_visibility="collapsed",
            placeholder="Paste the complete Job Description here, or click 'Try Sample JD' to test immediately...",
        )

    run_btn = st.button("✨ Optimize Resume & Calculate ATS Score", type="primary", use_container_width=True)

# --- Execution Pipeline ---
if run_btn:
    if not uploaded_pdf:
        st.error("⚠️ Please upload your base resume PDF first.")
        st.stop()

    resume_text = extract_text_from_pdf(uploaded_pdf.read())
    if resume_text.startswith("Error reading PDF"):
        st.error(resume_text)
        st.stop()

    jd_text = jd_manual_text.strip()
    if not jd_text and jd_url.strip():
        with st.spinner("🌐 Fetching Job Description from URL..."):
            jd_text = scrape_job_url(jd_url)

    if not jd_text:
        st.error("⚠️ Please paste a Job Description or click 'Try Sample JD'.")
        st.stop()

    start_time = time.time()
    with st.status("⚡ AI Agents Analyzing Resume & Target Role...", expanded=True) as status:
        try:
            initial_state = {
                "resume_text": resume_text,
                "jd_text": jd_text,
                "jd_analysis": {},
                "gap_report": {},
                "tailored_content": {},
                "status_log": [],
            }
            final_state = initial_state.copy()
            seen_logs = set()

            for step_output in resume_agent_app.stream(initial_state):
                for _, node_data in step_output.items():
                    final_state.update(node_data)
                    for log in node_data.get("status_log", []):
                        if log not in seen_logs:
                            st.markdown(log)
                            seen_logs.add(log)

            elapsed = round(time.time() - start_time, 1)
            status.update(
                label=f"✅ Resume Optimized in {elapsed}s!",
                state="complete",
                expanded=False,
            )
        except Exception as e:
            status.update(label="❌ Optimization Failed", state="error")
            st.error(f"Error: {str(e)}")
            st.stop()

    st.session_state["result"] = final_state
    st.session_state["candidate_name"] = candidate_name
    st.session_state["elapsed"] = elapsed
    st.rerun()

# --- Executive Results Dashboard ---
if "result" in st.session_state:
    res = st.session_state["result"]
    jd_info = res["jd_analysis"]
    gap = res["gap_report"]
    tailored = res["tailored_content"]
    score = gap.get("ats_score", 0)
    score_color = "#10B981" if score >= 75 else ("#F59E0B" if score >= 50 else "#F43F5E")

    # Compact 2x2 Mobile / 4-Column Desktop KPI Grid
    st.markdown(
        f"""
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">🎯 Target Role</div>
                <div class="kpi-value">{jd_info.get("role_title", "N/A")}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">🏢 Company</div>
                <div class="kpi-value">{jd_info.get("company_name", "N/A")}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">📊 ATS Match Score</div>
                <div class="kpi-value" style="color:{score_color};">{score}%</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">⚡ Processing Time</div>
                <div class="kpi-value">{st.session_state.get("elapsed", 0)}s</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.progress(min(max(score, 0), 100) / 100)

    tab1, tab2, tab3, tab4 = st.tabs([
        "📄 Tailored Resume",
        "📊 ATS Keyword Gap",
        "✉️ Cover Letter",
        "🏢 Company Intel",
    ])

    with tab1:
        st.markdown(
            f"""
            <div class="resume-sheet-card">
                <div style="font-size:0.78rem; font-weight:700; color:#818CF8; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:6px;">
                    ✨ ATS-Optimized Professional Summary
                </div>
                <div style="color:#F1F5F9; font-size:0.96rem; line-height:1.65;">
                    {tailored.get("custom_summary", "")}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2, gap="medium")
        with c1:
            st.markdown("#### 💼 Rewritten Experience Bullets")
            for b in tailored.get("rewritten_experience_bullets", []):
                st.markdown(f'<div class="bullet-card">• {b}</div>', unsafe_allow_html=True)
        with c2:
            st.markdown("#### 🛠️ Rewritten Project Bullets")
            for b in tailored.get("rewritten_project_bullets", []):
                st.markdown(f'<div class="bullet-card">• {b}</div>', unsafe_allow_html=True)

        st.divider()
        pdf_bytes = generate_tailored_pdf(
            st.session_state["candidate_name"],
            jd_info.get("role_title", "Role"),
            jd_info.get("company_name", "Company"),
            tailored,
        )
        st.download_button(
            label="📥 Download ATS-Ready Tailored Resume (PDF)",
            data=pdf_bytes,
            file_name=f"Tailored_Resume_{jd_info.get('company_name', 'Job').replace(' ', '_')}.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True,
        )

    with tab2:
        c1, c2 = st.columns(2, gap="medium")
        with c1:
            st.markdown("#### ✅ Matched Resume Skills")
            matched_html = "".join(
                f"<span class='skill-badge-match'>{s}</span>" for s in gap.get("matched_skills", [])
            )
            st.markdown(matched_html or "None detected", unsafe_allow_html=True)

        with c2:
            st.markdown("#### ⚠️ Missing Keywords Integrated")
            miss_html = "".join(
                f"<span class='skill-badge-miss'>{s}</span>" for s in gap.get("missing_keywords", [])
            )
            st.markdown(miss_html or "None missing", unsafe_allow_html=True)

        st.divider()
        st.markdown("#### 💡 Recruiter & ATS Optimization Tips")
        for tip in gap.get("improvement_suggestions", []):
            st.markdown(f'<div class="bullet-card">💡 {tip}</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown("#### ✉️ Tailored Cover Letter")
        st.text_area(
            "Ready to Copy",
            value=tailored.get("cover_letter", ""),
            height=300,
        )

    with tab4:
        st.markdown(f"#### 🏢 Live Company Research: {jd_info.get('company_name', '')}")
        st.markdown(jd_info.get("company_insights", ""))