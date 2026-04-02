from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from backend.database_connection import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)

    package_size = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey("categories.id"))
    image_path = Column(String, nullable=False)
    nutrient_type = Column(String, default="none")