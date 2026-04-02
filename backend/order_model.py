from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database_connection import Base


# -------------------------------
# ORDERS TABLE
# -------------------------------

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    total_amount = Column(Float, nullable=False)

    payment_method = Column(String, nullable=False)  # "cod" or "upi"

    payment_status = Column(String, default="pending")  
    # "pending" or "paid"

    order_status = Column(String, default="placed")  
    # "placed", "delivered", etc.

    delivery_name = Column(String, nullable=False)
    delivery_phone = Column(String, nullable=False)
    delivery_address = Column(String, nullable=False)
    delivery_city = Column(String, nullable=False)
    delivery_pincode = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to order items
    items = relationship("OrderItem", back_populates="order", cascade="all, delete")


# -------------------------------
# ORDER ITEMS TABLE
# -------------------------------

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)

    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    quantity = Column(Integer, nullable=False)

    price_at_purchase = Column(Float, nullable=False)

    # Relationship back to Order
    order = relationship("Order", back_populates="items")
    product = relationship("Product")