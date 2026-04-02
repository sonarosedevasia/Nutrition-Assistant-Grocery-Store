from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from backend.database_connection import Base


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    order_id = Column(Integer)

    rating = Column(Integer)

    comment = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())