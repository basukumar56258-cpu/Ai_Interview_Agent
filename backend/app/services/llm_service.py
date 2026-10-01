import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from groq import Groq

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


class AIServiceError(Exception):
	def __init__(self, message: str, status_code: int = 502):
		super().__init__(message)
		self.status_code = status_code


def missing_api_keys() -> list[str]:
	return [name for name in ("GROQ_API_KEY", "TAVILY_API_KEY") if not os.getenv(name)]


def require_ai_configuration() -> None:
	missing = missing_api_keys()
	if missing:
		raise AIServiceError(
			f"Please configure {' and '.join(missing)} in backend/.env.",
			status_code=503,
		)


def generate_completion(
	messages: list[dict[str, str]], *, json_mode: bool = False
) -> str:
	api_key = os.getenv("GROQ_API_KEY")
	if not api_key:
		raise AIServiceError(
			"Please configure GROQ_API_KEY and TAVILY_API_KEY in backend/.env.",
			status_code=503,
		)

	try:
		response = Groq(api_key=api_key, timeout=30.0, max_retries=1).chat.completions.create(
			model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
			messages=messages,
			temperature=0.4,
			response_format={"type": "json_object"} if json_mode else None,
		)
	except Exception as error:
		error_name = type(error).__name__
		status_code = getattr(error, "status_code", None)
		if error_name == "APITimeoutError":
			raise AIServiceError("The AI provider timed out. Please try again.", 504) from error
		if error_name == "RateLimitError" or status_code == 429:
			raise AIServiceError("The AI provider is rate limited. Please try again shortly.", 429) from error
		if error_name == "AuthenticationError" or status_code == 401:
			raise AIServiceError("The GROQ_API_KEY was rejected. Check backend/.env.", 401) from error
		if error_name == "APIConnectionError":
			raise AIServiceError("The AI provider is unreachable. Check your network and try again.", 503) from error
		raise AIServiceError("The AI provider could not complete this request. Please try again.") from error

	content: Any = response.choices[0].message.content
	return content if isinstance(content, str) else ""


def generate_json(messages: list[dict[str, str]]) -> dict[str, Any]:
	import json

	try:
		result = json.loads(generate_completion(messages, json_mode=True))
	except json.JSONDecodeError as error:
		raise AIServiceError("The AI provider returned an invalid response. Please try again.") from error
	if not isinstance(result, dict):
		raise AIServiceError("The AI provider returned an invalid response. Please try again.")
	return result
