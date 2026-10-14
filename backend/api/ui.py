from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import voice_notes as svc

router = APIRouter()
templates = Jinja2Templates(directory="backend/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: AsyncSession = Depends(get_db)):
    jobs = await svc.list_jobs(db)
    return templates.TemplateResponse("index.html", {"request": request, "title": "Voice Notes Summarizer", "jobs": jobs})

@router.post("/ui/jobs")
async def ui_job(title: str = Form(...), hint: str = Form(...), db: AsyncSession = Depends(get_db)):
    await svc.create_job(db, title, hint)
    return RedirectResponse("/", status_code=303)
