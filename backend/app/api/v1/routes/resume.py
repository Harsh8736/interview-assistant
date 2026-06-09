from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from datetime import datetime
from typing import Optional

from app.api.v1.dependencies.auth import get_current_user
from app.db.session import get_db
from app.db.models.interview import ResumeAnalysis
from app.services.resume.resume_parser import extract_text_from_pdf, parse_resume_sections
from app.services.resume.skill_matcher import analyze_resume_vs_jd

router = APIRouter()


@router.post("/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    job_description: str = Form(...),
    role_title: str = Form(...),
    interview_id: Optional[str] = Form(default=None),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Validate file type
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")

        # Clean up interview_id
        if not interview_id or interview_id.strip() in ["", "string", "null", "none"]:
            interview_id = None

        # Read and parse PDF
        file_bytes = await file.read()
        raw_text = extract_text_from_pdf(file_bytes)

        if not raw_text:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")

        # Parse into sections
        resume_sections = parse_resume_sections(raw_text)

        # Run 3-layer analysis
        analysis = await analyze_resume_vs_jd(
            resume_sections=resume_sections,
            job_description=job_description,
            role_title=role_title
        )

        # Save to DB
        resume_analysis = ResumeAnalysis(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            interview_id=interview_id,
            role_title=role_title,
            resume_text=raw_text,
            job_description=job_description,
            confidence_score=analysis.get("confidence_score"),
            analysis_result=analysis
        )
        db.add(resume_analysis)
        await db.commit()
        await db.refresh(resume_analysis)

        return {
            "analysis_id": resume_analysis.id,
            "confidence_score": analysis.get("confidence_score"),
            "skill_jd_match": analysis.get("skill_jd_match"),
            "project_jd_match": analysis.get("project_jd_match"),
            "skill_project_validation": analysis.get("skill_project_validation"),
            "confidence_breakdown": analysis.get("confidence_breakdown"),
            "gap_analysis": analysis.get("gap_analysis")
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis/{analysis_id}")
async def get_analysis(
    analysis_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ResumeAnalysis).where(ResumeAnalysis.id == analysis_id)
    )
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return analysis.analysis_result