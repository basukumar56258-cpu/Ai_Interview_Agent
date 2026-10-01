from app.services.llm_service import generate_completion


def generate_question(context: dict) -> str:
	return generate_completion(
		[
			{
				"role": "system",
				"content": "Ask exactly one clear interview question. Do not provide an answer or commentary.",
			},
			{"role": "user", "content": f"Interview context: {context}"},
		]
	).strip()
