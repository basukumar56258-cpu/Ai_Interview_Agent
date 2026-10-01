from app.services.llm_service import generate_json


def decide_followup(question: str, answer: str, evaluation: dict) -> dict:
	return generate_json(
		[
			{
				"role": "system",
				"content": "Decide whether one follow-up question would usefully clarify the candidate's answer. Return JSON with follow_up (boolean) and question (string). Do not force a follow-up when the answer is complete.",
			},
			{
				"role": "user",
				"content": f"Question: {question}\nAnswer: {answer}\nEvaluation: {evaluation}",
			},
		]
	)
