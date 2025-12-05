from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, String
from sqlalchemy.sql import func
from app.db.session import Base

class DVIRecord(Base):
    __tablename__ = "dvi_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    finance_score = Column(Float, nullable=False)
    logistics_score = Column(Float, nullable=False)
    health_score = Column(Float, nullable=False)
    education_score = Column(Float, nullable=False)
    wellbeing_score = Column(Float, nullable=False)

    overall_score = Column(Float, nullable=False)
    level = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
