from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.gemini_service import generate_plan

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title="FitBuddy – AI Fitness Plan Generator", version="1.0.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


class PlanRequest(BaseModel):
    goal: str = Field(min_length=2, max_length=40)
    level: str = Field(min_length=2, max_length=30)
    age: int = Field(ge=13, le=100)
    equipment: str = Field(min_length=1, max_length=80)
    minutes: int = Field(ge=10, le=180)
    days: int = Field(ge=3, le=7)
    diet: str = Field(min_length=1, max_length=80)
    notes: str = Field(default="", max_length=500)


@app.get("/")
def home():
    return FileResponse(BASE_DIR / "templates" / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "FitBuddy", "database": False}


@app.post("/api/generate-plan")
def create_plan(request: PlanRequest):
    try:
        return generate_plan(request.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Could not create plan: {exc}") from exc
