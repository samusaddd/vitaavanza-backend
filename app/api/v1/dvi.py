from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.dvi import DVICalculationInput, DVIRecordOut
from app.models.dvi import DVIRecord
from app.models.user import User
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger("dvi")

WEIGHTS = {
    "finance_score": 0.25,
    "logistics_score": 0.2,
    "health_score": 0.2,
    "education_score": 0.2,
    "wellbeing_score": 0.15,
}

def compute_overall_and_level(data: DVICalculationInput) -> tuple[float, str]:
    weighted_sum = (
        data.finance_score * WEIGHTS["finance_score"]
        + data.logistics_score * WEIGHTS["logistics_score"]
        + data.health_score * WEIGHTS["health_score"]
        + data.education_score * WEIGHTS["education_score"]
        + data.wellbeing_score * WEIGHTS["wellbeing_score"]
    )
    overall = weighted_sum

    if overall >= 80:
        level = "High"
    elif overall >= 50:
        level = "Medium"
    else:
        level = "Low"
    return overall, level

@router.post("/calculate", response_model=DVIRecordOut)
def calculate_dvi(
    payload: DVICalculationInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    overall, level = compute_overall_and_level(payload)

    record = DVIRecord(
        user_id=current_user.id,
        finance_score=payload.finance_score,
        logistics_score=payload.logistics_score,
        health_score=payload.health_score,
        education_score=payload.education_score,
        wellbeing_score=payload.wellbeing_score,
        overall_score=overall,
        level=level,
    )

    db.add(record)
    db.commit()
    db.refresh(record)
    logger.info(f"DVI calculated for user {current_user.email}: {overall:.1f} ({level})")
    return record
