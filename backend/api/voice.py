from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import voice_notes as svc
import json

class JobIn(BaseModel):
    title: str = Field(min_length=2)
    hint: str = Field(min_length=3, description="Simulated speech content")
    audio_ref: str = "file://note.m4a"

router = APIRouter()

@router.post("/jobs")
async def create_job(payload: JobIn, db: AsyncSession = Depends(get_db)):
    job = await svc.create_job(db, payload.title, payload.hint, payload.audio_ref)
    return {"id": job.id, "status": job.status}

@router.get("/jobs")
async def list_jobs(db: AsyncSession = Depends(get_db)):
    rows = await svc.list_jobs(db)
    return {"jobs": [{"id": j.id, "title": j.title, "status": j.status} for j in rows]}

@router.get("/jobs/{job_id}")
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)):
    job = await svc.get_job(db, job_id)
    if not job:
        raise HTTPException(404, "job not found")
    return {
        "id": job.id,
        "transcript": job.transcript,
        "summary": job.summary,
        "action_items": json.loads(job.action_items_json or "[]"),
        "status": job.status,
    }
