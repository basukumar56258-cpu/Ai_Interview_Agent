from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.agents.evaluator_agent import evaluate_answer
from app.agents.final_report_agent import build_report
from app.agents.followup_agent import decide_followup
from app.agents.interviewer_agent import generate_question
from app.agents.planner_agent import create_plan
from app.agents.profile_agent import analyze_profile
from app.models.schemas import AnswerRequest, InterviewCreate
from app.services.llm_service import require_ai_configuration
from app.services.research_service import research_job_description

router = APIRouter(prefix="/api/interview", tags=["interviews"])
interviews: dict[str, dict] = {}


@router.post("/create")
def create_interview(payload: InterviewCreate) -> dict:
	require_ai_configuration()
	research = research_job_description(payload.job_description)
	profile = analyze_profile(payload.resume_text, payload.job_description, research)
	plan = create_plan(profile, payload.question_count, payload.interview_type, payload.difficulty)
	questions = plan.get("questions")
	if not isinstance(questions, list):
		raise HTTPException(status_code=502, detail="The interview planner returned an invalid question plan.")
	questions = [str(question).strip() for question in questions if str(question).strip()]
	if not questions:
		raise HTTPException(status_code=502, detail="The interview planner did not return any questions.")

	interview_id = str(uuid4())
	context = {
		"job_description": payload.job_description,
		"interview_type": payload.interview_type,
		"difficulty": payload.difficulty,
		"profile": profile,
		"planned_question": questions[0],
		"question_number": 1,
	}
	first_question = generate_question(context)
	interviews[interview_id] = {
		"interview_id": interview_id,
		"status": "active",
		"profile": profile,
		"plan": questions[: payload.question_count],
		"question_index": 0,
		"current_question": first_question,
		"followup_used": False,
		"evaluations": [],
		"report": None,
	}
	return {
		"interview_id": interview_id,
		"status": "active",
		"first_question": first_question,
		"profile": profile,
		"question_count": len(interviews[interview_id]["plan"]),
	}


@router.get("/history")
def history() -> dict:
	return {
		"interviews": [
			{"interview_id": item["interview_id"], "status": item["status"]}
			for item in interviews.values()
		]
	}


@router.get("/{interview_id}")
def get_interview(interview_id: str) -> dict:
	interview = interviews.get(interview_id)
	if interview is None:
		raise HTTPException(status_code=404, detail="Interview not found.")
	return {
		"interview_id": interview_id,
		"status": interview["status"],
		"current_question": interview["current_question"],
	}


@router.post("/{interview_id}/answer")
def submit_answer(interview_id: str, payload: AnswerRequest) -> dict:
	interview = interviews.get(interview_id)
	if interview is None:
		raise HTTPException(status_code=404, detail="Interview not found.")
	if interview["status"] != "active":
		raise HTTPException(status_code=409, detail="This interview is already complete.")

	question = interview["current_question"]
	evaluation = evaluate_answer(question, payload.answer, interview["profile"])
	evaluation["question"] = question
	interview["evaluations"].append(evaluation)
	followup = decide_followup(question, payload.answer, evaluation)

	if followup.get("follow_up") and not interview["followup_used"]:
		next_question = generate_question(
			{
				"task": "Ask one follow-up based on the evaluation.",
				"original_question": question,
				"candidate_answer": payload.answer,
				"evaluation": evaluation,
				"follow_up_prompt": followup.get("question", ""),
			}
		)
		interview["followup_used"] = True
	else:
		interview["question_index"] += 1
		interview["followup_used"] = False
		if interview["question_index"] >= len(interview["plan"]):
			interview["status"] = "completed"
			interview["report"] = build_report(interview["evaluations"], interview["profile"])
			next_question = None
		else:
			next_question = generate_question(
				{
					"task": "Ask the next planned interview question.",
					"planned_question": interview["plan"][interview["question_index"]],
					"profile": interview["profile"],
					"question_number": interview["question_index"] + 1,
				}
			)

	interview["current_question"] = next_question
	return {
		"interview_id": interview_id,
		"status": interview["status"],
		"evaluation": evaluation,
		"next_question": next_question,
		"report": interview["report"],
	}


@router.post("/{interview_id}/finish")
def finish_interview(interview_id: str) -> dict:
	interview = interviews.get(interview_id)
	if interview is None:
		raise HTTPException(status_code=404, detail="Interview not found.")
	if interview["report"] is None:
		interview["report"] = build_report(interview["evaluations"], interview["profile"])
	interview["status"] = "completed"
	return {"interview_id": interview_id, "status": "completed", "report": interview["report"]}


@router.get("/{interview_id}/report")
def report(interview_id: str) -> dict:
	interview = interviews.get(interview_id)
	if interview is None:
		raise HTTPException(status_code=404, detail="Interview not found.")
	if interview["report"] is None:
		raise HTTPException(status_code=404, detail="The interview report is not ready.")
	return {"interview_id": interview_id, "report": interview["report"]}
