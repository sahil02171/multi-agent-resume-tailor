from pydantic import BaseModel, Field


class JDAnalysis(BaseModel):
    role_title: str = Field(description="Exact job title from the JD")
    company_name: str = Field(description="Company name hiring for this role")
    required_skills: list[str] = Field(description="Must-have technical and domain skills")
    preferred_skills: list[str] = Field(description="Nice-to-have or bonus skills")
    key_responsibilities: list[str] = Field(description="Core job duties")
    company_insights: str = Field(description="Summary of company tech stack, products, and culture")


class GapReport(BaseModel):
    ats_score: int = Field(description="Estimated ATS match score from 0 to 100")
    matched_skills: list[str] = Field(description="Skills present in both resume and JD")
    missing_keywords: list[str] = Field(description="Important JD keywords missing from the resume")
    improvement_suggestions: list[str] = Field(description="Actionable tips to improve resume alignment")


class TailoredContent(BaseModel):
    custom_summary: str = Field(description="Tailored 3-4 line professional summary aligned to the JD")
    rewritten_experience_bullets: list[str] = Field(description="ATS-optimized experience bullet points")
    rewritten_project_bullets: list[str] = Field(description="ATS-optimized project bullet points")
    cover_letter: str = Field(description="Personalized, concise cover letter for this company and role")
    