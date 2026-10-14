# Dev server for voice-notes-summarizer
$env:LLM_MODE = "mock"
uvicorn backend.main:app --reload --port 8000
