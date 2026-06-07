from pydantic import BaseModel
from typing import Optional


class InterviewStartRequest(BaseModel):
    role_title: str
    job_description: str


class InterviewStartResponse(BaseModel):
    session_id: str
    first_question: str
    role_title: str


class AnswerSubmitRequest(BaseModel):
    session_id: str
    question: str
    answer: str


class AnswerFeedback(BaseModel):
    score: float
    feedback: str
    next_question: Optional[str] = None
    is_complete: bool
    total_score: Optional[float] = None


class InterviewReport(BaseModel):
    session_id: str
    role_title: str
    status: str
    total_score: float
    total_questions: int
    completed_at: Optional[str] = None
    answers: list[dict]