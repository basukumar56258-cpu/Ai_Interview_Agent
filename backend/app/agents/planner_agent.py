from app.services.llm_service import generate_json


def create_plan(
	profile: dict, question_count: int, interview_type: str, difficulty: str
) -> dict:
	return generate_json(
		[
			{
				"role": "system",
				"content": "Create an interview plan. Return JSON with a questions array containing concise, distinct interview questions, exactly the requested number. Tailor them to the candidate profile and role.",
			},
			{
				"role": "user",
				"content": f"Question count: {question_count}\nInterview type: {interview_type}\nDifficulty: {difficulty}\nCandidate profile: {profile}",
			},
		]
	)
