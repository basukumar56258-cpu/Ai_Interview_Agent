from app.services.llm_service import generate_json


def evaluate_answer(question: str, answer: str, profile: dict) -> dict:
	return generate_json(
		[
			{
				"role": "system",
				"content": "Evaluate the candidate's answer fairly against the question and role context. Return JSON with score (number from 0 to 100), feedback (specific string), and missing_points (array of strings). Do not reward unsupported claims.",
			},
			{
				"role": "user",
				"content": f"Question: {question}\nAnswer: {answer}\nCandidate profile: {profile}",
			},
		]
	)
