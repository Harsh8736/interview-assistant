import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

# --- Generate Interview Questions ---
question_prompt = PromptTemplate(
    input_variables=["job_role", "job_description"],
    template="""
    You are an expert technical interviewer.
    Generate 5 interview questions for the role: {job_role}.
    Job Description: {job_description}
    Return only a numbered list of 5 questions. Nothing else.
    """
)

question_chain = question_prompt | llm

# --- Evaluate Answer ---
evaluate_prompt = PromptTemplate(
    input_variables=["question", "answer", "job_role"],
    template="""
    You are an expert interview coach.
    Role: {job_role}
    Question: {question}
    Candidate's Answer: {answer}

    Evaluate the answer using the STAR method (Situation, Task, Action, Result).
    Give:
    1. A score out of 10
    2. What was good
    3. What was missing
    4. An improved version of the answer
    """
)

evaluate_chain = evaluate_prompt | llm

# --- Parse Resume ---
resume_prompt = PromptTemplate(
    input_variables=["resume_text"],
    template="""
    You are an expert resume parser.
    Extract the following from the resume:
    1. Name
    2. Skills (list)
    3. Projects (list with 1 line description each)
    4. Experience (list)
    5. Education

    Resume:
    {resume_text}

    Return a clean structured summary.
    """
)

resume_chain = resume_prompt | llm