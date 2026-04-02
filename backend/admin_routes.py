from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database_connection import get_db
from backend.user_model import User
from backend.product_model import Product
from backend.category_model import Category
from backend.order_model import Order

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])


@router.get("/dashboard-stats")
def get_dashboard_stats(db: Session = Depends(get_db)):

    
    total_users = db.query(User).filter(User.role == "user").count()
    total_products = db.query(Product).count()
    total_categories = db.query(Category).count()
    total_orders = db.query(Order).count()

    pending_orders = db.query(Order).filter(
        Order.order_status == "placed"
    ).count()

    revenue = db.query(func.sum(Order.total_amount)).filter(
        Order.payment_status == "paid"
    ).scalar()

    return {
        "total_users": total_users,
        "total_products": total_products,
        "total_categories": total_categories,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "revenue": round(revenue or 0, 2)
    }