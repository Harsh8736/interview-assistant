import fitz  # pymupdf
import re
from typing import Optional


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract raw text from PDF bytes using pymupdf."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text.strip()


def parse_resume_sections(raw_text: str) -> dict:
    """
    Split resume text into sections:
    - skills
    - experience
    - projects
    - education
    """
    sections = {
        "skills": "",
        "experience": "",
        "projects": "",
        "education": "",
        "raw": raw_text
    }

    # Normalize text
    text = raw_text

    # Section headers to detect (case insensitive)
    section_patterns = {
        "skills": r"(technical skills|skills|technologies)",
        "experience": r"(experience|work experience|professional experience|internship)",
        "projects": r"(projects|personal projects|academic projects)",
        "education": r"(education|academic background|qualifications)"
    }

    lines = text.split("\n")
    current_section = None
    section_content = {k: [] for k in sections}

    for line in lines:
        line_lower = line.strip().lower()
        matched = False
        for section, pattern in section_patterns.items():
            if re.search(pattern, line_lower):
                current_section = section
                matched = True
                break
        if not matched and current_section:
            section_content[current_section].append(line)

    for section in section_content:
        sections[section] = "\n".join(section_content[section]).strip()

    return sections