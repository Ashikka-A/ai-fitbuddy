# FitBuddy AI Fitness Planner

A database-free fitness planner with a FastAPI backend and HTML/CSS/JavaScript frontend.

- Frontend: `templates/index.html`, `static/style.css`, `static/app.js`
- Backend: `app/main.py`
- Optional Gemini integration: `app/gemini_service.py`
- No SQLite, SQLAlchemy, migrations, or user database.
- If `GEMINI_API_KEY` is blank or Gemini is unavailable, the built-in planner still returns a complete plan.

## Run on Windows CMD

```cmd
cd /d "YOUR\\FitBuddy-AI"
py -3.14 -m venv .venv
.venv\\Scripts\\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
python -m uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000

Never put a real API key into source control. `.env` is ignored by Git.
