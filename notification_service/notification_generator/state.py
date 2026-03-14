from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class GeneratorState(Base):
    __tablename__ = "notification_generator_state"

    job_name = Column(String, primary_key=True)
    last_processed_at = Column(DateTime(timezone=True), nullable=False)
    version = Column(String, nullable=False)
