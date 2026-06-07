import uuid
import json
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.interview import Interview, InterviewAnswer
from app.services.ai.gemini_service import generate_first_question, evaluate_answer


async def start_interview_session(
    user_id: str,
    role_title: str,
    job_description: str,
    db: AsyncSession
) -> dict:
    # Gemini se pehla question lo
    first_question = await generate_first_question(role_title, job_description)

    # DB mein Interview row banao
    interview = Interview(
        id=str(uuid.uuid4()),
        user_id=user_id,
        role_title=role_title,
        job_description=job_description,
        status="active"
    )
    db.add(interview)
    await db.commit()
    await db.refresh(interview)

    return {
        "session_id": interview.id,
        "first_question": first_question,
        "role_title": role_title
    }


async def process_answer(
    session_id: str,
    question: str,
    answer: str,
    db: AsyncSession
) -> dict:
    # Interview fetch karo DB se
    result = await db.execute(
        select(Interview).where(Interview.id == session_id)
    )
    interview = result.scalar_one_or_none()

    if not interview:
        raise ValueError("Session not found")

    if interview.status == "completed":
        raise ValueError("Interview already completed")

    # Kitne answers ho chuke hain count karo
    answers_result = await db.execute(
        select(InterviewAnswer).where(InterviewAnswer.interview_id == session_id)
    )
    existing_answers = answers_result.scalars().all()
    question_number = len(existing_answers) + 1

    # Gemini se evaluate karo
    eval_result = await evaluate_answer(
        interview.role_title,
        question,
        answer,
        question_number
    )

    # Answer DB mein save karo
    interview_answer = InterviewAnswer(
        id=str(uuid.uuid4()),
        interview_id=session_id,
        question_number=question_number,
        question=question,
        answer=answer,
        score=eval_result["score"],
        feedback=eval_result["feedback"]
    )
    db.add(interview_answer)

    is_complete = question_number >= 5

    if is_complete:
        # Final score calculate karo
        all_scores = [a.score for a in existing_answers] + [eval_result["score"]]
        avg_score = sum(all_scores) / len(all_scores)

        interview.status = "completed"
        interview.total_score = avg_score
        interview.completed_at = datetime.utcnow()
        interview.final_report = {
            "total_score": avg_score,
            "total_questions": 5,
            "answers": [
                {
                    "question_number": a.question_number,
                    "question": a.question,
                    "answer": a.answer,
                    "score": a.score,
                    "feedback": a.feedback
                }
                for a in existing_answers
            ] + [{
                "question_number": question_number,
                "question": question,
                "answer": answer,
                "score": eval_result["score"],
                "feedback": eval_result["feedback"]
            }]
        }

    await db.commit()

    return {
        "score": eval_result["score"],
        "feedback": eval_result["feedback"],
        "next_question": eval_result.get("next_question") if not is_complete else None,
        "is_complete": is_complete,
        "total_score": interview.total_score if is_complete else None
    }


async def get_interview_report(session_id: str, db: AsyncSession) -> dict:
    result = await db.execute(
        select(Interview).where(Interview.id == session_id)
    )
    interview = result.scalar_one_or_none()

    if not interview:
        raise ValueError("Interview not found")

    # Fetch all answers regardless of status
    answers_result = await db.execute(
        select(InterviewAnswer)
        .where(InterviewAnswer.interview_id == session_id)
        .order_by(InterviewAnswer.question_number)
    )
    answers = answers_result.scalars().all()

    answers_data = [
        {
            "question_number": a.question_number,
            "question": a.question,
            "answer": a.answer,
            "score": a.score,
            "feedback": a.feedback
        }
        for a in answers
    ]

    avg_score = (
        sum(a.score for a in answers) / len(answers)
        if answers else 0.0
    )

    return {
        "session_id": session_id,
        "role_title": interview.role_title,
        "status": interview.status,
        "total_score": interview.total_score if interview.status == "completed" else avg_score,
        "total_questions": len(answers),
        "completed_at": interview.completed_at.isoformat() if interview.completed_at else None,
        "answers": answers_data
    }