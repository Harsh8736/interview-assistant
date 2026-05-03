from pydantic import BaseModel

class QuestionRequest(BaseModel):
    job_role: str
    job_description: str = ""

class AnswerRequest(BaseModel):
    question: str
    answer: str
    job_role: str

class ResumeRequest(BaseModel):
    resume_text: str