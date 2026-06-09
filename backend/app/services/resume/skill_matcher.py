import json
from groq import Groq
from app.core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)


async def analyze_resume_vs_jd(
    resume_sections: dict,
    job_description: str,
    role_title: str
) -> dict:
    """
    3-layer analysis:
    1. Skill-to-JD match
    2. Project-to-JD match
    3. Skill-to-Project validation (is the skill backed by a project?)
    """

    prompt = f"""
You are an expert technical recruiter and resume analyst.

ROLE: {role_title}

JOB DESCRIPTION:
{job_description}

CANDIDATE RESUME:

SKILLS SECTION:
{resume_sections.get('skills', 'Not found')}

PROJECTS SECTION:
{resume_sections.get('projects', 'Not found')}

EXPERIENCE SECTION:
{resume_sections.get('experience', 'Not found')}

Perform a 3-layer analysis and respond ONLY in this exact JSON format:

{{
    "skill_jd_match": {{
        "matched_skills": ["skill1", "skill2"],
        "missing_skills": ["skill3", "skill4"],
        "match_percentage": <number 0-100>
    }},
    "project_jd_match": {{
        "relevant_projects": ["project name and why it matches"],
        "missing_project_areas": ["areas JD requires but no project covers"],
        "match_percentage": <number 0-100>
    }},
    "skill_project_validation": [
        {{
            "skill": "skill name",
            "in_skills_section": true,
            "backed_by_project": true,
            "project_evidence": "project name where this skill is used or null"
        }}
    ],
    "confidence_score": <weighted number 0-100>,
    "confidence_breakdown": {{
        "skill_match_weight": 40,
        "project_match_weight": 40,
        "skill_project_validation_weight": 20,
        "explanation": "brief explanation of the score"
    }},
    "gap_analysis": {{
        "critical_gaps": ["most important missing skills/experience"],
        "strengths": ["what candidate does well for this role"],
        "recommendations": ["what candidate should add/improve"]
    }}
}}

Confidence score formula:
- skill_jd_match percentage * 0.4
- project_jd_match percentage * 0.4  
- % of skills backed by projects * 0.2

Return only valid JSON, nothing else.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000
    )

    text = response.choices[0].message.content.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)