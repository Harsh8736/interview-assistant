from fastapi import FastAPI
from models import QuestionRequest, AnswerRequest, ResumeRequest
from chains import question_chain, evaluate_chain, resume_chain

app = FastAPI(
    title="AI Interview Assistant",
    description="LLM-powered mock interview API using LangChain + Gemini",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "AI Interview Assistant is running 🚀"}

@app.post("/generate-questions")
def generate_questions(request: QuestionRequest):
    response = question_chain.invoke({
        "job_role": request.job_role,
        "job_description": request.job_description
    })
    return {"questions": response.content}

@app.post("/evaluate-answer")
def evaluate_answer(request: AnswerRequest):
    response = evaluate_chain.invoke({
        "question": request.question,
        "answer": request.answer,
        "job_role": request.job_role
    })
    return {"feedback": response.content}

@app.post("/parse-resume")
def parse_resume(request: ResumeRequest):
    response = resume_chain.invoke({
        "resume_text": request.resume_text
    })
    return {"parsed": response.content}