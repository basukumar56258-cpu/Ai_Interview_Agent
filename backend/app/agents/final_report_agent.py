from app.services.llm_service import generate_json


def build_report(evaluations: list, profile: dict) -> dict:
	return generate_json(
		[
			{
				"role": "system",
				"content": "Summarize the completed interview. Return JSON with overall_score (number from 0 to 100), strengths (array), improvements (array), and recommendations (array). Base all findings on the supplied evaluations.",
			},
			{
				"role": "user",
				"content": f"Candidate profile: {profile}\nInterview evaluations: {evaluations}",
			},
		]
	)
