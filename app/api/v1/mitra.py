from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Literal
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.services.mitra import generate_mitra_response

router = APIRouter()

class MitraMessage(BaseModel):
    role: Literal["user", "assistant"] = "user"
    content: str

class MitraChatRequest(BaseModel):
    messages: List[MitraMessage]

class MitraChatResponse(BaseModel):
    reply: str

@router.post("/chat", response_model=MitraChatResponse)
def chat_with_mitra(
    payload: MitraChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    filtered_messages = [
        {"role": m.role, "content": m.content}
        for m in payload.messages
    ]

    reply = generate_mitra_response(
        user=current_user,
        messages=filtered_messages,
        db=db,
    )

    return MitraChatResponse(reply=reply)
