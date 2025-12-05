from pydantic import BaseModel
from typing import Optional

class OpportunityBase(BaseModel):
    title: str
    category: str
    short_description: str
    full_description: Optional[str] = None
    location: Optional[str] = None
    link: Optional[str] = None
    relevance_min_dvi: Optional[float] = None

class OpportunityCreate(OpportunityBase):
    pass

class OpportunityOut(OpportunityBase):
    id: int

    class Config:
        from_attributes = True
