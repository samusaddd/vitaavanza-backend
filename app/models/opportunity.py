from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from sqlalchemy.sql import func
from app.db.session import Base

class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False)
    short_description = Column(String, nullable=False)
    full_description = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    link = Column(String, nullable=True)
    relevance_min_dvi = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
