from fpdf import FPDF


def _clean_text(text: str) -> str:
    """Replaces special Unicode characters so standard PDF fonts render cleanly without errors."""
    replacements = {
        "\u2013": "-",
        "\u2014": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2022": "*",
        "\u2026": "...",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.encode("latin-1", "replace").decode("latin-1")


def generate_tailored_pdf(
    candidate_name: str,
    role_title: str,
    company_name: str,
    tailored_data: dict,
) -> bytes:
    """Creates a clean, single-column ATS-friendly PDF resume and returns raw bytes."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Header
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 8, _clean_text(candidate_name or "Tailored Resume"), ln=True, align="C")

    pdf.set_font("Helvetica", "I", 10)
    subtitle = f"Target Role: {role_title} | {company_name}"
    pdf.cell(0, 6, _clean_text(subtitle), ln=True, align="C")
    pdf.ln(4)

    # Professional Summary
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 7, "PROFESSIONAL SUMMARY", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5.5, _clean_text(tailored_data.get("custom_summary", "")))
    pdf.ln(4)

    # Experience Bullets
    exp_bullets = tailored_data.get("rewritten_experience_bullets", [])
    if exp_bullets:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 7, "RELEVANT EXPERIENCE", ln=True)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(2)
        pdf.set_font("Helvetica", "", 10)
        for bullet in exp_bullets:
            pdf.multi_cell(0, 5.5, _clean_text(f"- {bullet}"))
            pdf.ln(1)
        pdf.ln(3)

    # Project Bullets
    proj_bullets = tailored_data.get("rewritten_project_bullets", [])
    if proj_bullets:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 7, "KEY TECHNICAL PROJECTS", ln=True)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(2)
        pdf.set_font("Helvetica", "", 10)
        for bullet in proj_bullets:
            pdf.multi_cell(0, 5.5, _clean_text(f"- {bullet}"))
            pdf.ln(1)

    return bytes(pdf.output())