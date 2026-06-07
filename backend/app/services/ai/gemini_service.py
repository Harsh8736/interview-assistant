from groq import Groq
from app.core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

async def generate_first_question(role_title: str, job_description: str) -> str:
    try:
        prompt = f"""
        You are an expert technical interviewer for the role: {role_title}
        
        Job Description: {job_description}
        
        Generate ONE strong opening interview question for this role.
        Return only the question, nothing else.
        """
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"GROQ ERROR: {e}")
        raise e


async def evaluate_answer(
    role_title: str,
    question: str,
    answer: str,
    question_number: int
) -> dict:
    prompt = f"""
    You are an expert interviewer for: {role_title}
    
    Question asked: {question}
    Candidate's answer: {answer}
    
    Evaluate the answer and respond in this exact JSON format:
    {{
        "score": <number 1-10>,
        "feedback": "<2-3 lines of constructive feedback>",
        "next_question": "<next interview question or null if this was question 5>"
    }}
    
    This is question number {question_number} out of 5.
    If question_number is 5, set next_question to null.
    Return only valid JSON, nothing else.
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    import json
    text = response.choices[0].message.content.strip().replace("```json", "").replace("```", "")
    return json.loads(text)