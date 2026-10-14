from __future__ import annotations
import json
import re
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.llm import get_llm
from backend.models import AudioJob
from backend.repositories import audit
from backend.utils.ids import short_id

_SENT = re.compile(r"[.!?]+")

def _mock_transcript(hint: str) -> str:
    hint = hint.strip() or "Team sync about roadmap."
    parts = [p.strip() for p in _SENT.split(hint) if p.strip()]
    lines = [f"Speaker A: {p}." for p in parts[:6]]
    return "\n".join(lines)

async def create_job(session: AsyncSession, title: str, hint: str, audio_ref: str = "file://note.m4a") -> AudioJob:
    job = AudioJob(id=short_id(), title=title[:160], audio_ref=audio_ref[:240], status="queued")
    session.add(job)
    await session.commit()
    await session.refresh(job)
    audit.record("audio_job_created", job.id)
    await process_job(session, job.id, hint)
    return job

async def process_job(session: AsyncSession, job_id: str, hint: str) -> AudioJob:
    job = await session.get(AudioJob, job_id)
    if not job:
        raise ValueError("job not found")
    job.status = "transcribing"
    job.transcript = _mock_transcript(hint)
    await session.commit()
    llm = get_llm()
    job.status = "summarizing"
    summary = await llm.complete(job.transcript, system="Summarize voice note in 2 sentences.")
    job.summary = summary[:2000]
    structured = await llm.complete_json(
        job.transcript + "\nReturn JSON with action_items list of strings.",
        system="Extract tasks",
    )
    items = structured.get("action_items") if isinstance(structured, dict) else None
    if not items:
        items = [ln.split(":", 1)[-1].strip() for ln in job.transcript.split("\n") if ln.strip()][:3]
    job.action_items_json = json.dumps(items)
    job.status = "done"
    await session.commit()
    await session.refresh(job)
    return job

async def list_jobs(session: AsyncSession) -> list[AudioJob]:
    return list((await session.execute(select(AudioJob).order_by(AudioJob.created_at.desc()))).scalars())

async def get_job(session: AsyncSession, job_id: str) -> AudioJob | None:
    return await session.get(AudioJob, job_id)
