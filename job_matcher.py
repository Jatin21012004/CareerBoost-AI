from sentence_transformers import SentenceTransformer, util
import numpy as np
from typing import List, Dict, Tuple

model = SentenceTransformer('all-MiniLM-L6-v2')

# Skill weights (higher = more important)
SKILL_WEIGHTS = {
    # Technical Skills
    'python': 1.5,
    'java': 1.3,
    'c++': 1.2,
    'machine learning': 1.8,
    'data analysis': 1.6,
    'sql': 1.4,
    'aws': 1.5,
    
    # Tools
    'tableau': 1.3,
    'power bi': 1.3,
    'excel': 1.1,
    
    # Soft Skills
    'communication': 1.2,
    'leadership': 1.4,
    'problem-solving': 1.3
}

def match_resume_to_job(resume_text: str, job_description: str) -> float:
    """
    Calculate match score with semantic similarity + weighted skills.
    Returns score (0-100) where:
    - 0-40: Poor match
    - 41-70: Good match  
    - 71-100: Excellent match
    """
    # Semantic similarity (original approach)
    resume_emb = model.encode(resume_text, convert_to_tensor=True)
    job_emb = model.encode(job_description, convert_to_tensor=True)
    semantic_score = float(util.pytorch_cos_sim(resume_emb, job_emb)[0][0]) * 100
    
    # Skill-based matching (weighted)
    resume_skills = extract_skills_from_text(resume_text)
    job_skills = extract_skills_from_text(job_description)
    skill_score = calculate_skill_score(resume_skills, job_skills)
    
    # Combined score (70% semantic, 30% skills)
    return round(0.7 * semantic_score + 0.3 * skill_score, 2)

def extract_skills_from_text(text: str) -> List[str]:
    """Extract skills with multi-word support using regex."""
    skills = []
    text_lower = text.lower()
    
    # Check multi-word skills first
    for skill in SKILL_WEIGHTS.keys():
        if ' ' in skill and skill in text_lower:
            skills.append(skill)
    
    # Check single-word skills
    single_words = set(text_lower.split())
    for skill in SKILL_WEIGHTS.keys():
        if ' ' not in skill and skill in single_words:
            skills.append(skill)
    
    return list(set(skills))

def calculate_skill_score(resume_skills: List[str], job_skills: List[str]) -> float:
    """
    Calculate weighted skill match (0-100).
    Formula: (sum of matched skill weights) / (sum of required skill weights) * 100
    """
    if not job_skills:
        return 100.0  # No skills required = perfect match
    
    matched_weights = sum(SKILL_WEIGHTS.get(skill, 1.0) 
                         for skill in resume_skills 
                         if skill in job_skills)
    
    total_weights = sum(SKILL_WEIGHTS.get(skill, 1.0) 
                    for skill in job_skills)
    
    return (matched_weights / total_weights) * 100

# Bonus: Skill gap analysis
def get_skill_gaps(resume_skills: List[str], job_skills: List[str]) -> Dict[str, float]:
    """
    Returns missing skills with their importance weights.
    Useful for suggestion engine.
    """
    return {
        skill: SKILL_WEIGHTS.get(skill, 1.0)
        for skill in job_skills
        if skill not in resume_skills
    }