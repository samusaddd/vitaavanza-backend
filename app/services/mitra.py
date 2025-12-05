from typing import List, Dict
from sqlalchemy.orm import Session
from openai import OpenAI

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.dvi import DVIRecord
from app.models.user import User

settings = get_settings()
logger = get_logger("mitra")

client = OpenAI(api_key=settings.openai_api_key)

def build_user_context(user: User, db: Session) -> str:
    last_dvi = (
        db.query(DVIRecord)
        .filter(DVIRecord.user_id == user.id)
        .order_by(DVIRecord.created_at.desc())
        .first()
    )

    dvi_summary = "No DVI data yet."
    if last_dvi:
        dvi_summary = (
            f"Latest DVI — overall: {last_dvi.overall_score:.1f} "
            f"({last_dvi.level}), finance: {last_dvi.finance_score:.1f}, "
            f"logistics: {last_dvi.logistics_score:.1f}, health: {last_dvi.health_score:.1f}, "
            f"education: {last_dvi.education_score:.1f}, wellbeing: {last_dvi.wellbeing_score:.1f}."
        )

    role_sentence = {
        "user": "an individual student or young worker.",
        "institution": "a partner institution user.",
        "admin": "a VitaAvanza core team member.",
    }.get(user.role, "a VitaAvanza user.")

    return (
        f"The user is {user.full_name or 'an anonymous VitaAvanza user'} ({role_sentence}) "
        f"with email {user.email}. {dvi_summary} "
        "You are Mitra, VitaAvanza's AI assistant. You answer in a clear, structured, step-by-step way, "
        "always focusing on: (1) reducing stress, (2) unlocking opportunities, and (3) improving the user's DVI."
    )

def generate_mitra_response(
    user: User,
    messages: List[Dict[str, str]],
    db: Session,
) -> str:
    if not settings.openai_api_key:
        logger.error("OPENAI_API_KEY is not set.")
        return "Mitra is temporarily unavailable because the system is not configured with an OpenAI API key."

    system_prompt = build_user_context(user, db)
    chat_messages = [{"role": "system", "content": system_prompt}] + messages

    completion = client.chat.completions.create(
        model=settings.openai_model,
        messages=chat_messages,
        temperature=0.7,
    )

    reply = completion.choices[0].message.content
    logger.info("Mitra reply generated.")
    return reply
