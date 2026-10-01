import json
import re
from typing import Any

from app.config import GEMINI_API_KEY, GEMINI_MODEL


def _fallback_plan(data: dict[str, Any]) -> dict[str, Any]:
    goal = data["goal"]
    level = data["level"]
    days = data["days"]
    equipment = data["equipment"]
    minutes = data["minutes"]

    goal_focus = {
        "Weight loss": "moderate-to-high calorie expenditure with full-body movements",
        "Muscle gain": "progressive resistance training with adequate recovery",
        "Strength": "compound movements with controlled repetitions and longer rests",
        "General fitness": "balanced strength, mobility and cardiovascular training",
    }.get(goal, "balanced training")

    equipment_note = "bodyweight only" if equipment == "None" else equipment
    templates = [
        ("Full Body A", ["Squats", "Push-ups", "Glute bridges", "Plank"]),
        ("Full Body B", ["Reverse lunges", "Pike push-ups", "Hip hinges", "Dead bug"]),
        ("Conditioning", ["Marching/high knees", "Mountain climbers", "Bodyweight squats", "Bird dog"]),
        ("Upper Body + Core", ["Push-ups", "Shoulder taps", "Triceps dips", "Side plank"]),
        ("Lower Body", ["Squats", "Reverse lunges", "Calf raises", "Glute bridges"]),
        ("Mobility + Recovery", ["Cat-cow", "Hip flexor stretch", "Hamstring stretch", "Child's pose"]),
        ("Active Recovery", ["Easy walk", "Light mobility", "Breathing practice", "Gentle stretching"]),
    ]
    workouts = []
    for i in range(days):
        name, exercises = templates[i % len(templates)]
        if i == days - 1:
            name = "Recovery & Mobility"
            exercises = templates[5][1]
        workouts.append({
            "day": i + 1,
            "title": name,
            "duration": minutes,
            "focus": goal_focus,
            "exercises": [
                {"name": ex, "sets": 3 if ex not in ("Plank", "Side plank", "Dead bug", "Bird dog") else 2,
                 "reps": "8-15" if ex not in ("Plank", "Side plank") else "30-45 sec"}
                for ex in exercises
            ],
        })

    return {
        "title": f"{days}-Day {goal} Plan",
        "summary": f"A {level.lower()} plan focused on {goal.lower()}, using {equipment_note}, with sessions of about {minutes} minutes.",
        "workouts": workouts,
        "nutrition": [
            "Build meals around vegetables or fruit, a protein source, whole grains or other high-fibre carbohydrates, and healthy fats.",
            "Drink water regularly and adjust intake for heat, activity and thirst.",
            "For muscle gain, include a protein-rich food at each main meal and maintain enough overall energy intake.",
            "Keep highly processed snacks and sugary drinks occasional rather than making them the base of your diet.",
        ],
        "recovery": [
            "Aim for consistent sleep and a regular bedtime/wake time.",
            "Use at least one easier day each week and stop an exercise if it causes sharp or unusual pain.",
            "Increase repetitions, resistance or time gradually instead of making large jumps.",
        ],
        "source": "Built-in FitBuddy planner",
    }


def _extract_json(text: str) -> dict[str, Any] | None:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        value = json.loads(text)
        return value if isinstance(value, dict) else None
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                value = json.loads(match.group(0))
                return value if isinstance(value, dict) else None
            except json.JSONDecodeError:
                return None
    return None


def generate_plan(data: dict[str, Any]) -> dict[str, Any]:
    if not GEMINI_API_KEY:
        return _fallback_plan(data)

    try:
        from google import genai

        client = genai.Client(api_key=GEMINI_API_KEY)
        schema = {
            "title": "string",
            "summary": "string",
            "workouts": [{
                "day": "integer", "title": "string", "duration": "integer", "focus": "string",
                "exercises": [{"name": "string", "sets": "integer", "reps": "string"}]
            }],
            "nutrition": ["string"],
            "recovery": ["string"],
            "source": "string"
        }
        prompt = f"""Create a safe, practical {data['days']}-day fitness plan.
User goal: {data['goal']}
Experience: {data['level']}
Age: {data['age']}
Equipment: {data['equipment']}
Workout minutes: {data['minutes']}
Diet preference: {data['diet']}
Extra notes: {data['notes'] or 'None'}

Return ONLY valid JSON matching this shape exactly:
{json.dumps(schema)}
Use sensible beginner/intermediate exercise volumes. Do not diagnose medical conditions or prescribe medication. Keep nutrition general, not a medical diet."""
        response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        result = _extract_json(response.text or "")
        if result and result.get("workouts"):
            result["source"] = f"Gemini ({GEMINI_MODEL})"
            return result
    except Exception:
        pass

    fallback = _fallback_plan(data)
    fallback["source"] = "Built-in FitBuddy planner (AI service unavailable)"
    return fallback
