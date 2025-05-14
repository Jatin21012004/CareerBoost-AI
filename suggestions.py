from typing import List, Dict
from job_matcher import get_skill_gaps  # Import from our upgraded job_matcher.py

def generate_suggestions(resume_data: Dict, match_score: float, job_description: str = "") -> List[str]:
    """
    Generates personalized resume suggestions based on:
    - Missing key skills
    - Resume structure issues
    - Job description requirements
    - Match score analysis
    """
    suggestions = []
    
    # 1. Score-based suggestions
    if match_score < 40:
        suggestions.append("🔴 **Major Improvement Needed**: Your resume has low alignment with this job's requirements.")
    elif match_score < 70:
        suggestions.append("🟡 **Good Start**: Tailor your resume further to stand out.")
    else:
        suggestions.append("🟢 **Strong Match**: Focus on highlighting your top 3 most relevant skills.")

    # 2. Skill-related suggestions (if we have job description)
    if job_description:
        job_skills = extract_skills_from_text(job_description)
        missing_skills = get_skill_gaps(resume_data.get("skills", []), job_skills)
        
        if missing_skills:
            # Get top 3 most important missing skills
            top_missing = sorted(missing_skills.items(), key=lambda x: x[1], reverse=True)[:3]
            suggestions.append("🧠 **Top Missing Skills**: " + 
                             ", ".join([f"{skill} (priority: {weight}x)" 
                                      for skill, weight in top_missing]))
    
    # 3. Structure suggestions
    sections = resume_data.get("sections", {})
    
    if not sections.get("experience"):
        suggestions.append("📌 **Add Work Experience**: Include at least 2-3 relevant positions.")
    elif len(sections["experience"].split('\n')) < 3:
        suggestions.append("📌 **Expand Work Experience**: Add bullet points with metrics like 'Increased X by Y%'")
    
    if not sections.get("education"):
        suggestions.append("🎓 **Add Education**: Include degree, university, and graduation year.")
    
    # 4. Content quality suggestions
    if "skills" in resume_data:
        if len(resume_data["skills"]) < 5:
            suggestions.append("🛠️ **Diversify Skills**: List both technical and soft skills (aim for 8-10 total).")
        if all(len(skill) < 4 for skill in resume_data["skills"]):
            suggestions.append("ℹ️ **Specify Skills**: Replace abbreviations like 'JS' with 'JavaScript'")

    # 5. Contact info check
    if not resume_data.get("email"):
        suggestions.append("✉️ **Add Professional Email**: Use a Gmail/Outlook address with your name.")
    if not resume_data.get("phone"):
        suggestions.append("📱 **Add Phone Number**: Include with country code if applying internationally.")

    # 6. Advanced suggestions for good resumes
    if match_score > 65:
        suggestions.extend([
            "✨ **Pro Tip**: Add a 'Key Achievements' section with 2-3 bullet points",
            "✨ **Pro Tip**: Include relevant certifications if available"
        ])

    return suggestions

# Helper function to maintain compatibility
def extract_skills_from_text(text: str) -> List[str]:
    """Reuse the skill extraction logic from job_matcher"""
    from job_matcher import extract_skills_from_text as extract_skills
    return extract_skills(text)