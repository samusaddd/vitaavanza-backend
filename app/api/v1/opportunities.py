from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.schemas.opportunity import OpportunityCreate, OpportunityOut
from app.models.opportunity import Opportunity

router = APIRouter()

@router.post("/", response_model=OpportunityOut)
def create_opportunity(
    payload: OpportunityCreate,
    db: Session = Depends(get_db),
):
    opp = Opportunity(**payload.model_dump())
    db.add(opp)
    db.commit()
    db.refresh(opp)
    return opp

@router.get("/", response_model=List[OpportunityOut])
def list_opportunities(
    db: Session = Depends(get_db),
    min_dvi: Optional[float] = None,
):
    q = db.query(Opportunity)
    if min_dvi is not None:
        q = q.filter(
            (Opportunity.relevance_min_dvi == None)  # noqa: E711
            | (Opportunity.relevance_min_dvi <= min_dvi)
        )
    return q.order_by(Opportunity.created_at.desc()).all()
