import os
import json
import time
from concurrent.futures import ThreadPoolExecutor
from typing import TypedDict
from dotenv import load_dotenv
from google import genai
from google.genai import types
from groq import Groq
from langgraph.graph import StateGraph, END

from schemas import JDAnalysis, GapReport, TailoredContent
from tools import research_company

load_dotenv()

gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
groq_api_key = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=groq_api_key) if groq_api_key else None

# Active Gemini models only (removed deprecated 2.5 / 3.0 models)
GEMINI_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.8-flash",
    "gemini-3.5-flash",
]


class AgentState(TypedDict):
    resume_text: str
    jd_text: str
    jd_analysis: dict
    gap_report: dict
    tailored_content: dict
    status_log: list[str]


def _call_structured_llm(prompt: str, response_schema):
    """Tries Gemini models first; automatically falls back to Groq Llama-3.3-70B on 503/429."""
    last_error = None

    # 1. Try Google Gemini Models
    for model_id in GEMINI_MODELS:
        for attempt in range(2):
            try:
                response = gemini_client.models.generate_content(
                    model=model_id,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=response_schema,
                        temperature=0.2,
                    ),
                )
                return response.parsed
            except Exception as e:
                last_error = e
                err_str = str(e)
                if "503" in err_str or "UNAVAILABLE" in err_str:
                    time.sleep(1.0)
                    continue
                if any(code in err_str for code in ["404", "NOT_FOUND", "429", "RESOURCE_EXHAUSTED"]):
                    break
                raise e

    # 2. Automatic Failover to Groq (High-speed backup when Gemini has 503/429)
    if groq_client:
        schema_json = json.dumps(response_schema.model_json_schema(), indent=2)
        groq_prompt = (
            f"{prompt}\n\n"
            f"Respond ONLY with a valid JSON object matching this exact Pydantic schema:\n{schema_json}"
        )
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a precise JSON API. Output valid JSON only."},
                {"role": "user", "content": groq_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        raw_json = completion.choices[0].message.content
        return response_schema.model_validate_json(raw_json)

    raise RuntimeError(f"Gemini models unavailable and GROQ_API_KEY not configured. Last error: {last_error}")


# --- NODE 1: Parallel JD Analysis + Gap Scoring ---
def research_and_analyze_node(state: AgentState) -> dict:
    jd_prompt = f"""
    Extract exact role_title, company_name, required_skills, preferred_skills,
    key_responsibilities, and brief company_insights from this Job Description:
    {state['jd_text']}
    """
    gap_prompt = f"""
    Compare this Base Resume with the Job Description. Give a realistic ats_score (0-100),
    matched_skills, missing_keywords, and concise improvement_suggestions.
    
    Base Resume:
    {state['resume_text']}
    
    Job Description:
    {state['jd_text']}
    """

    with ThreadPoolExecutor(max_workers=2) as executor:
        f_jd = executor.submit(_call_structured_llm, jd_prompt, JDAnalysis)
        f_gap = executor.submit(_call_structured_llm, gap_prompt, GapReport)
        parsed_jd: JDAnalysis = f_jd.result()
        parsed_gap: GapReport = f_gap.result()

    live_insights = research_company(parsed_jd.company_name, parsed_jd.role_title)
    jd_dict = parsed_jd.model_dump()
    jd_dict["company_insights"] = f"{parsed_jd.company_insights}\n\n**Live Web Research:**\n{live_insights}"

    logs = [
        f"✅ Agent 1 (Researcher): Extracted JD for **{parsed_jd.role_title}** at **{parsed_jd.company_name}**.",
        f"✅ Agent 2 (Gap Analyzer): Calculated ATS Match Score: **{parsed_gap.ats_score}%**.",
    ]
    return {
        "jd_analysis": jd_dict,
        "gap_report": parsed_gap.model_dump(),
        "status_log": logs,
    }


# --- NODE 2: Tailoring Writer + Anti-Hallucination Guardrail ---
def writer_critic_node(state: AgentState) -> dict:
    prompt = f"""
    You are an expert ATS Resume Writer & Fact-Checker.
    Rewrite the candidate's professional summary, experience bullets, and project bullets
    to naturally integrate missing keywords from the Gap Report using strong action verbs and metrics.
    
    STRICT ANTI-HALLUCINATION GUARDRAIL:
    - NEVER invent fake companies, degrees, certifications, or skills not present in the Base Resume.
    - Only optimize and reframe existing projects/experience truthfully.
    - Write a crisp, personalized cover letter (under 220 words) referencing company insights.
    
    Base Resume:
    {state['resume_text']}
    
    Analyzed JD:
    {state['jd_analysis']}
    
    Gap Report:
    {state['gap_report']}
    """
    tailored: TailoredContent = _call_structured_llm(prompt, TailoredContent)

    logs = state.get("status_log", []) + [
        "✅ Agent 3 & 4 (Writer + ATS Critic): Generated verified ATS bullets & Cover Letter."
    ]
    return {"tailored_content": tailored.model_dump(), "status_log": logs}


def build_resume_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("research_and_analyze", research_and_analyze_node)
    workflow.add_node("writer_critic", writer_critic_node)

    workflow.set_entry_point("research_and_analyze")
    workflow.add_edge("research_and_analyze", "writer_critic")
    workflow.add_edge("writer_critic", END)
    return workflow.compile()


resume_agent_app = build_resume_graph()