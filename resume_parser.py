import re
import spacy
from datetime import datetime
from typing import Dict, List, Optional
import PyPDF2
import docx2txt

# Load SpaCy English model
import subprocess
import spacy

# Load SpaCy model, download it if not available
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=True)
    nlp = spacy.load("en_core_web_sm")


def extract_text_from_pdf(file) -> str:
    """Extract text from PDF with error handling."""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        return "".join(page.extract_text() or "" for page in pdf_reader.pages)
    except Exception as e:
        return f"[PDF Error: {str(e)}]"

def extract_text_from_docx(file) -> str:
    """Extract text from DOCX."""
    return docx2txt.process(file)

def parse_resume(text: str) -> Dict[str, any]:
    doc = nlp(text)
    
    # --- Name Extraction ---
    name = next((ent.text for ent in doc.ents if ent.label_ == "PERSON"), "")

    # --- Contact Info ---
    email = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    phone = re.search(r'(\+?\d{1,3}[-\.\s]?)?\(?\d{3}\)?[-\.\s]?\d{3}[-\.\s]?\d{4}', text)

    # --- Skills (Multi-Word Aware) ---
    skill_patterns = [
        r"(?i)\b(python|java|c\+\+|javascript)\b",
        r"(?i)\b(machine learning|data analysis|data science)\b",
        r"(?i)\b(communication|leadership|problem solving)\b",
        r"(?i)\b(sql|mysql|postgresql)\b",
        r"(?i)\b(html|css|react|angular)\b"
    ]
    skills = []
    for pattern in skill_patterns:
        skills.extend([match.lower() for match in re.findall(pattern, text)])
    skills = list(set(skills))  # Remove duplicates

    # --- Education (Degree + University) ---
    education = []
    edu_pattern = r"(?i)((B\.?S\.?|B\.?Tech|M\.?S\.?|Ph\.?D)[\w\s]*?)(?:at|from|,)\s*([\w\s]+?(?:University|Institute|College))"
    for match in re.finditer(edu_pattern, text):
        degree, uni = match.groups()
        education.append(f"{degree.strip()} from {uni.strip()}")

    # --- Experience (Job Titles + Duration) ---
    experience = []
    exp_pattern = r"(?i)([\w\s]+?(?:Engineer|Developer|Analyst|Specialist))\s*(?:at|,)\s*([\w\s]+?)(?:\s*\((\d{4})\s*-\s*(\d{4}|Present)\))?"
    for match in re.finditer(exp_pattern, text):
        title, company, start, end = match.groups()
        duration = f"({start}-{end})" if start else ""
        experience.append(f"{title.strip()} at {company.strip()} {duration}")

    # --- Section Detection (Fallback) ---
    sections = {
        "education": "\n".join(education) if education else "",
        "experience": "\n".join(experience) if experience else "",
        "skills": ", ".join(skills),
        "projects": ""
    }

    return {
        "name": name,
        "email": email.group() if email else "",
        "phone": phone.group() if phone else "",
        "skills": skills,
        "education": education,
        "experience": experience,
        "sections": sections  # Backward compatibility
    }
