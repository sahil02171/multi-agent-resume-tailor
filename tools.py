import streamlit as st
import os
import re
import pymupdf as fitz
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

_RESEARCH_CACHE = {}


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extracts clean text from uploaded PDF bytes."""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        pages_text = [page.get_text("text") for page in doc]
        doc.close()
        raw_text = "\n".join(pages_text)
        return re.sub(r"\n{3,}", "\n\n", raw_text).strip()
    except Exception as e:
        return f"Error reading PDF: {str(e)}"


def scrape_job_url(url: str) -> str:
    """Scrapes readable job description text from a public URL."""
    if not url or not url.strip():
        return ""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(url.strip(), headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = soup.get_text(separator=" ")
        clean_text = re.sub(r"\s+", " ", text).strip()
        return clean_text[:8000]
    except Exception:
        return ""


def research_company(company_name: str, role_title: str) -> str:
    """Fetches company tech stack and recent engineering insights via Tavily with caching."""
    api_key = os.getenv("TAVILY_API_KEY") or (st.secrets["TAVILY_API_KEY"] if "TAVILY_API_KEY" in st.secrets else None)
    if not api_key or not company_name or company_name.lower() in ["unknown", "n/a", "not specified", ""]:
        return "No company specified in JD; skipped live web search."

    cache_key = f"{company_name.lower()}_{role_title.lower()}"
    if cache_key in _RESEARCH_CACHE:
        return _RESEARCH_CACHE[cache_key]

    try:
        client = TavilyClient(api_key=api_key)
        result = client.search(
            query=f"{company_name} tech stack engineering culture {role_title}",
            search_depth="basic",
            max_results=2,
        )
        snippets = [
            f"- **{r.get('title', '')}**: {r.get('content', '')[:250]}..."
            for r in result.get("results", [])
        ]
        summary = "\n".join(snippets) if snippets else "No recent public insights found."
        _RESEARCH_CACHE[cache_key] = summary
        return summary
    except Exception:
        return "Company research skipped due to timeout."