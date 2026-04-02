from sqlalchemy import Column, Integer, String
from backend.database_connection import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    image_path = Column(String, nullable=False)
