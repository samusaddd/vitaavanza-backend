from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY) if (OpenAI and OPENAI_API_KEY) else None

app = FastAPI(
    title="VitaAvanza Backend",
    version="0.2.0",
    description="API for DVI and Mitra (VitaAvanza pilot)",
)

# CORS – allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production, restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- MODELS ----------

class DVIRequest(BaseModel):
    """
    DVI pillars – all on a 0–100 scale.
    """
    stability: float
    growth: float
    wellbeing_load: float
    social_support: float


class DVIBreakdown(BaseModel):
    stability: float
    growth: float
    wellbeing_load: float
    social_support: float


class DVIResponse(BaseModel):
    overall: float
    breakdown: DVIBreakdown
    commentary: str


class ChatMessage(BaseModel):
    role: str   # "user", "assistant", "system"
    content: str


class DVISuggestion(BaseModel):
    stability: float
    growth: float
    wellbeing_load: float
    social_support: float


class MitraRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = None


class MitraResponse(BaseModel):
    reply: str
    dvi_suggestion: Optional[DVISuggestion] = None


# ---------- UTILS ----------

def clamp(value: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
    return max(min_val, min(max_val, value))


def infer_dvi_from_text(text: str) -> DVISuggestion:
    """
    Very simple heuristic that converts text into a rough DVI suggestion.
    This is just for the pilot – later this can be replaced by a real model.
    """
    t = text.lower()

    stability = 70.0
    growth = 70.0
    wellbeing_load = 70.0
    social_support = 70.0

    # Money / rent / job stress → hurts stability
    if any(word in t for word in ["rent", "bills", "money", "debt", "can't pay", "unemployed", "no job"]):
        stability -= 20
        wellbeing_load += 10  # more pressure

    # Exams / study / deadlines → growth pressure + wellbeing load
    if any(word in t for word in ["exam", "session", "thesis", "deadline", "university", "study"]):
        growth -= 10
        wellbeing_load += 10

    # Stress / burnout / anxiety → higher wellbeing load
    if any(word in t for word in ["anxiety", "panic", "burnout", "tired", "exhausted", "overwhelmed", "stressed"]):
        wellbeing_load += 15

    # Social isolation → lower social support
    if any(word in t for word in ["alone", "no friends", "isolated", "lonely", "nobody"]):
        social_support -= 15

    # Clamp values
    stability = clamp(stability, 10, 95)
    growth = clamp(growth, 10, 95)
    wellbeing_load = clamp(wellbeing_load, 10, 95)
    social_support = clamp(social_support, 10, 95)

    return DVISuggestion(
        stability=stability,
        growth=growth,
        wellbeing_load=wellbeing_load,
        social_support=social_support,
    )


# ---------- ROUTES ----------

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "vitaavanza-backend"}


@app.post("/api/dvi/score", response_model=DVIResponse)
def compute_dvi(payload: DVIRequest):
    """
    DVI = [Stability, Growth, Wellbeing Load, Social Support] → 0–100 index.
    Weights inspired by your spec.
    """
    stability = clamp(payload.stability)
    growth = clamp(payload.growth)
    wellbeing_load = clamp(payload.wellbeing_load)
    social_support = clamp(payload.social_support)

    # Higher wellbeing_load means more pressure, so we invert it for the total score
    normalized_wellbeing = 100 - wellbeing_load

    overall = (
        0.30 * stability +
        0.30 * growth +
        0.25 * normalized_wellbeing +
        0.15 * social_support
    )

    if overall >= 80:
        commentary = "You are in a strong development zone. Let’s keep reinforcing what already works."
    elif overall >= 60:
        commentary = "You have a solid base with some pressure points. We should prioritise 1–2 weaker pillars."
    elif overall >= 40:
        commentary = "You are in a fragile phase. We should design a concrete plan across stability, growth, and support."
    else:
        commentary = "Critical support needed. VitaAvanza should activate all available tools, services, and mentors for you."

    return DVIResponse(
        overall=round(overall, 1),
        breakdown=DVIBreakdown(
            stability=stability,
            growth=growth,
            wellbeing_load=wellbeing_load,
            social_support=social_support,
        ),
        commentary=commentary,
    )


@app.post("/api/mitra/chat", response_model=MitraResponse)
async def mitra_chat(req: MitraRequest):
    """
    Mitra – female persona, AI assistant.
    - Reads the conversation
    - Replies as Mitra (she/her)
    - Also returns a DVI suggestion based on the user message (for the pilot)
    """
    # If no OpenAI key → soft fallback
    if not openai_client:
        dvi_suggestion = infer_dvi_from_text(req.message)
        reply_text = (
            "Ciao, sono Mitra 💜\n\n"
            "Al momento il motore AI completo non è configurato sul server, "
            "ma posso comunque darti un’idea di come il tuo DVI potrebbe reagire "
            "alla situazione che hai descritto.\n\n"
            "Usa il pulsante 'Applica suggerimento di Mitra' per aggiornare i tuoi valori DVI."
        )
        return MitraResponse(
            reply=reply_text,
            dvi_suggestion=dvi_suggestion,
        )

    messages: List[Dict[str, str]] = [
        {
            "role": "system",
            "content": (
                "You are Mitra, a female AI assistant of VitaAvanza. "
                "You speak as 'I' and use she/her pronouns. "
                "You help students, young workers, and migrants plan their life: "
                "money, exams, work shifts, health logistics, and bureaucracy. "
                "You are kind, practical, structured, and never judgmental. "
                "Always think in terms of the four DVI pillars: Stability, Growth, "
                "Wellbeing Load, Social Support, but explain things in human language."
            ),
        }
    ]

    if req.history:
        for m in req.history:
            messages.append({"role": m.role, "content": m.content})

    messages.append({"role": "user", "content": req.message})

    try:
        completion = openai_client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            temperature=0.4,
        )
        reply_text = completion.choices[0].message.content.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mitra error: {e}")

    dvi_suggestion = infer_dvi_from_text(req.message)

    return MitraResponse(
        reply=reply_text,
        dvi_suggestion=dvi_suggestion,
    )
