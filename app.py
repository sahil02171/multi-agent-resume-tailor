import time
import streamlit as st
from tools import extract_text_from_pdf, scrape_job_url
from agents import resume_agent_app
from pdf_generator import generate_tailored_pdf

st.set_page_config(
    page_title="AI Resume Tailor | Multi-Agent Studio",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- Responsive & Modern SaaS CSS ---
st.markdown(
    """
    <style>
    /* Clean container padding for both Mobile & Desktop */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 1150px !important;
    }

    /* Hero Header Banner */
    .hero-banner {
        background: linear-gradient(135deg, #1E1B4B 0%, #312E81 50%, #0F172A 100%);
        border: 1px solid rgba(99, 102, 241, 0.35);
        border-radius: 16px;
        padding: 1.5rem 1.75rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
    }
    .hero-title {
        font-size: 1.75rem;
        font-weight: 800;
        color: #FFFFFF;
        margin: 0 0 0.35rem 0;
        line-height: 1.25;
    }
    .hero-subtitle {
        font-size: 0.95rem;
        color: #C7D2FE;
        margin: 0;
    }

    /* Glass KPI Cards */
    .kpi-card {
        background: #131A2A;
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 14px;
        padding: 1rem 1.15rem;
        text-align: left;
        margin-bottom: 0.75rem;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .kpi-card:hover {
        border-color: #6366F1;
        transform: translateY(-2px);
    }
    .kpi-label {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94A3B8;
        margin-bottom: 0.25rem;
    }
    .kpi-value {
        font-size: 1.25rem;
        font-weight: 700;
        color: #F8FAFC;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* Content Cards */
    .content-card {
        background: #131A2A;
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 14px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }

    /* Skill Badges */
    .skill-badge-match {
        display: inline-block;
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.4);
        color: #6EE7B7;
        padding: 5px 12px;
        border-radius: 999px;
        margin: 4px 4px 4px 0;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .skill-badge-miss {
        display: inline-block;
        background: rgba(244, 63, 94, 0.15);
        border: 1px solid rgba(244, 63, 94, 0.4);
        color: #FDA4AF;
        padding: 5px 12px;
        border-radius: 999px;
        margin: 4px 4px 4px 0;
        font-size: 0.85rem;
        font-weight: 500;
    }

    /* Mobile & Tablet Responsive Overrides */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.9rem !important;
            padding-right: 0.9rem !important;
            padding-top: 1rem !important;
        }
        .hero-banner {
            padding: 1.15rem 1.2rem;
            border-radius: 12px;
        }
        .hero-title {
            font-size: 1.35rem;
        }
        .hero-subtitle {
            font-size: 0.85rem;
        }
        .kpi-value {
            font-size: 1.1rem;
        }
        /* Scrollable horizontal tabs on small phone screens */
        .stTabs [data-baseweb="tab-list"] {
            gap: 6px;
            overflow-x: auto;
            flex-wrap: nowrap;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 0.82rem;
            padding: 8px 12px;
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

# --- Hero Header ---
st.markdown(
    """
    <div class="hero-banner">
        <div class="hero-title"> Multi-Agent Resume & Company Intel Studio</div>
        <div class="hero-subtitle">Parallel LangGraph Agents • Google Gemini Structured AI • Live Tavily Web Research</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Main Screen Responsive Input Panel (Works cleanly on Phone & Laptop) ---
has_result = "result" in st.session_state
with st.expander("📤 Step 1: Upload Resume & Target Job Details", expanded=not has_result):
    col_left, col_right = st.columns([1, 1.3], gap="large")

    with col_left:
        candidate_name = st.text_input("👤 Your Full Name", value="Sahil Raj")
        uploaded_pdf = st.file_uploader("📄 Upload Base Resume (PDF)", type=["pdf"])
        jd_url = st.text_input("🔗 Job Posting URL (Optional)", placeholder="https://careers.company.com/...")

    with col_right:
        top_row1, top_row2 = st.columns([1.4, 1])
        with top_row1:
            st.markdown("**📝 Target Job Description**")
        with top_row2:
            if st.button("⚡ Load Sample JD", use_container_width=True):
                st.session_state["sample_jd"] = SAMPLE_JD

        jd_manual_text = st.text_area(
            "Job Description",
            value=st.session_state.get("sample_jd", ""),
            height=175,
            label_visibility="collapsed",
            placeholder="Paste the full Job Description here, or tap 'Load Sample JD' to test instantly...",
        )

    run_btn = st.button("✨ Generate Tailored Resume & ATS Report", type="primary", use_container_width=True)

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
        with st.spinner("🌐 Extracting Job Description from URL..."):
            jd_text = scrape_job_url(jd_url)

    if not jd_text:
        st.error("⚠️ Please paste a Job Description or click 'Load Sample JD'.")
        st.stop()

    start_time = time.time()
    with st.status("⚡ Running Parallel Multi-Agent Workflow...", expanded=True) as status:
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
                label=f"✅ Done in {elapsed}s! All 4 Agents Verified.",
                state="complete",
                expanded=False,
            )
        except Exception as e:
            status.update(label="❌ Agent Pipeline Failed", state="error")
            st.error(f"Error: {str(e)}")
            st.stop()

    st.session_state["result"] = final_state
    st.session_state["candidate_name"] = candidate_name
    st.session_state["elapsed"] = elapsed
    st.rerun()

# --- Results Dashboard ---
if "result" in st.session_state:
    res = st.session_state["result"]
    jd_info = res["jd_analysis"]
    gap = res["gap_report"]
    tailored = res["tailored_content"]
    score = gap.get("ats_score", 0)

    # Responsive 4-Card KPI Grid
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-label">Target Role</div>'
            f'<div class="kpi-value">{jd_info.get("role_title", "N/A")}</div></div>',
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-label">Company</div>'
            f'<div class="kpi-value">{jd_info.get("company_name", "N/A")}</div></div>',
            unsafe_allow_html=True,
        )
    with k3:
        score_color = "#10B981" if score >= 75 else ("#F59E0B" if score >= 50 else "#F43F5E")
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-label">ATS Match Score</div>'
            f'<div class="kpi-value" style="color:{score_color};">{score}%</div></div>',
            unsafe_allow_html=True,
        )
    with k4:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-label">AI Speed</div>'
            f'<div class="kpi-value">{st.session_state.get("elapsed", 0)}s</div></div>',
            unsafe_allow_html=True,
        )

    st.progress(min(max(score, 0), 100) / 100)

    tab1, tab2, tab3, tab4 = st.tabs([
        "📄 Tailored Resume",
        "📊 ATS Gap Analysis",
        "✉️ Cover Letter",
        "🏢 Company Intel",
    ])

    with tab1:
        st.markdown(
            f'<div class="content-card"><h4>✨ Tailored Professional Summary</h4>'
            f'<p style="color:#E2E8F0; line-height:1.6;">{tailored.get("custom_summary", "")}</p></div>',
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2, gap="medium")
        with c1:
            st.subheader("💼 Optimized Experience")
            for b in tailored.get("rewritten_experience_bullets", []):
                st.markdown(f"- {b}")
        with c2:
            st.subheader("🛠️ Optimized Projects")
            for b in tailored.get("rewritten_project_bullets", []):
                st.markdown(f"- {b}")

        st.divider()
        pdf_bytes = generate_tailored_pdf(
            st.session_state["candidate_name"],
            jd_info.get("role_title", "Role"),
            jd_info.get("company_name", "Company"),
            tailored,
        )
        st.download_button(
            label="📥 Download ATS-Friendly Tailored PDF",
            data=pdf_bytes,
            file_name=f"Tailored_Resume_{jd_info.get('company_name', 'Job').replace(' ', '_')}.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True,
        )

    with tab2:
        c1, c2 = st.columns(2, gap="medium")
        with c1:
            st.subheader("✅ Matched Skills")
            matched_html = "".join(
                f"<span class='skill-badge-match'>{s}</span>" for s in gap.get("matched_skills", [])
            )
            st.markdown(matched_html or "None detected", unsafe_allow_html=True)

        with c2:
            st.subheader("⚠️ Keywords Integrated")
            miss_html = "".join(
                f"<span class='skill-badge-miss'>{s}</span>" for s in gap.get("missing_keywords", [])
            )
            st.markdown(miss_html or "None missing", unsafe_allow_html=True)

        st.divider()
        st.subheader("💡 Actionable Resume Tips")
        for tip in gap.get("improvement_suggestions", []):
            st.markdown(f"- {tip}")

    with tab3:
        st.subheader("✉️ Personalized Cover Letter")
        st.text_area(
            "Ready to Copy",
            value=tailored.get("cover_letter", ""),
            height=300,
        )

    with tab4:
        st.subheader(f"🏢 Live Web Research: {jd_info.get('company_name', '')}")
        st.markdown(jd_info.get("company_insights", ""))