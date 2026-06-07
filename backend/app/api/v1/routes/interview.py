from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.interview import (
    InterviewStartRequest,
    InterviewStartResponse,
    AnswerSubmitRequest,
    AnswerFeedback
)
from app.services.interview.interview_service import (
    start_interview_session,
    process_answer,
    get_interview_report
)
from app.api.v1.dependencies.auth import get_current_user
from app.db.session import get_db

router = APIRouter()


@router.post("/start", response_model=InterviewStartResponse)
async def start_interview(
    request: InterviewStartRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await start_interview_session(
            user_id=current_user.id,
            role_title=request.role_title,
            job_description=request.job_description,
            db=db
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/answer", response_model=AnswerFeedback)
async def submit_answer(
    request: AnswerSubmitRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await process_answer(
            session_id=request.session_id,
            question=request.question,
            answer=request.answer,
            db=db
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report/{session_id}")
async def get_report(
    session_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        report = await get_interview_report(session_id, db)
        return report
    except ValueError as e:
        status_code = 404 if "not found" in str(e).lower() else 400
        raise HTTPException(status_code=status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))