import os

from tavily import TavilyClient

from app.services.llm_service import AIServiceError


def research_job_description(job_description: str) -> str:
	api_key = os.getenv("TAVILY_API_KEY")
	if not api_key:
		raise AIServiceError(
			"Please configure GROQ_API_KEY and TAVILY_API_KEY in backend/.env.",
			status_code=503,
		)

	try:
		response = TavilyClient(api_key=api_key).search(
			query=f"Current technologies, responsibilities, and interview topics for: {job_description[:500]}",
			search_depth="basic",
			max_results=5,
		)
	except Exception as error:
		error_name = type(error).__name__
		status_code = getattr(error, "status_code", None)
		if error_name in {"Timeout", "TimeoutError", "ReadTimeout"}:
			raise AIServiceError("Web research timed out. Please try again.", 504) from error
		if status_code == 401 or "Auth" in error_name or "InvalidAPIKey" in error_name:
			raise AIServiceError("The TAVILY_API_KEY was rejected. Check backend/.env.", 401) from error
		if status_code == 429 or "RateLimit" in error_name:
			raise AIServiceError("Web research is rate limited. Please try again shortly.", 429) from error
		raise AIServiceError("Web research is unavailable. Check your network and try again.", 503) from error

	results = response.get("results", [])
	snippets = [
		f"{item.get('title', '')}: {item.get('content', '')}"
		for item in results
		if isinstance(item, dict) and item.get("content")
	]
	return "\n".join(snippets)[:6000] or "No relevant research results were found."
