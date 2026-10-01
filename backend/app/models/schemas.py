from typing import Literal

from pydantic import BaseModel, Field, field_validator


class InterviewCreate(BaseModel):
	job_description: str = Field(min_length=1, max_length=20000)
	interview_type: Literal["Mixed", "Technical", "Behavioral"] = "Mixed"
	difficulty: Literal["Adaptive", "Easy", "Medium", "Hard"] = "Adaptive"
	question_count: int = Field(default=10, ge=1, le=20)
	resume_text: str = Field(default="", max_length=30000)

	@field_validator("job_description")
	@classmethod
	def validate_job_description(cls, value: str) -> str:
		value = value.strip()
		if not value:
			raise ValueError("Job description is required.")
		return value


class AnswerRequest(BaseModel):
	answer: str = Field(min_length=1, max_length=10000)

	@field_validator("answer")
	@classmethod
	def validate_answer(cls, value: str) -> str:
		value = value.strip()
		if not value:
			raise ValueError("Answer cannot be empty.")
		return value
