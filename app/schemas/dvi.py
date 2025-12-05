from pydantic import BaseModel
from typing import Optional

class DVICalculationInput(BaseModel):
    finance_score: float
    logistics_score: float
    health_score: float
    education_score: float
    wellbeing_score: float

class DVIRecordOut(BaseModel):
    id: int
    user_id: int
    finance_score: float
    logistics_score: float
    health_score: float
    education_score: float
    wellbeing_score: float
    overall_score: float
    level: str

    class Config:
        from_attributes = True
