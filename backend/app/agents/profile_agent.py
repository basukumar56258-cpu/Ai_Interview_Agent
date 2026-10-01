from app.services.llm_service import generate_json


def analyze_profile(resume_text: str, job_description: str, research_notes: str) -> dict:
    return generate_json(
        [
            {
                "role": "system",
                "content": "Analyze the candidate against the role. Return JSON with skills (array), experience (string), projects (array), skill_gaps (array), and match_notes (array). Do not invent candidate experience.",
            },
            {
                "role": "user",
                "content": f"JOB DESCRIPTION:\n{job_description}\n\nRESUME:\n{resume_text or 'No resume provided.'}\n\nROLE RESEARCH:\n{research_notes}",
            },
        ]
    )
