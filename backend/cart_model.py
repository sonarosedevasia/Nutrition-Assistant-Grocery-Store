from sqlalchemy import Column, Integer, ForeignKey
from backend.database_connection import Base


class Cart(Base):
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, index=True)

    # Which user owns this cart item
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Which product is added
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # How many quantity
    quantity = Column(Integer, nullable=False, default=1)