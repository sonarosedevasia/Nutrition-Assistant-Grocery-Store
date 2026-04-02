from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database_connection import get_db
from backend.jwt_utils import get_current_user
from backend.user_model import User
from backend.cart_model import Cart
from backend.order_model import Order, OrderItem

router = APIRouter(prefix="/users", tags=["Users"])


# ===============================
# GET CURRENT USER DETAILS
# ===============================
@router.get("/me")
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == current_user["id"]).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "name": user.name,
        "email": user.email,
        "phone": user.phone
    }


# ===============================
# UPDATE PROFILE
# ===============================
@router.put("/update")
def update_profile(
    name: str,
    phone: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == current_user["id"]).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.name = name
    user.phone = phone

    db.commit()

    return {"message": "Profile updated successfully"}


# ===============================
# DELETE ACCOUNT (HARD DELETE)
# ===============================
@router.delete("/delete")
def delete_account(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == current_user["id"]).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Delete cart
    db.query(Cart).filter(Cart.user_id == user.id).delete()

    # Delete order items first
    orders = db.query(Order).filter(Order.user_id == user.id).all()
    for order in orders:
        db.query(OrderItem).filter(OrderItem.order_id == order.id).delete()

    # Delete orders
    db.query(Order).filter(Order.user_id == user.id).delete()

    # Delete user
    db.delete(user)

    db.commit()

    return {"message": "Account deleted successfully"}




from sqlalchemy import func
from backend.order_model import Order


# ===============================
# ADMIN - GET ALL USERS
# ===============================
@router.get("/admin/all-users")
def get_all_users(db: Session = Depends(get_db)):

    users = db.query(User).all()

    result = []

    for user in users:

        if user.role == "admin":
            continue

        order_count = db.query(func.count(Order.id)).filter(
            Order.user_id == user.id
        ).scalar()

        result.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "orders": order_count
        })

    return result
from backend.order_model import Order, OrderItem
from backend.cart_model import Cart


# ===============================
# DELETE MY ACCOUNT
# ===============================
@router.delete("/delete-me")
def delete_my_account(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    user_id = current_user["id"]

    # delete order items
    orders = db.query(Order).filter(Order.user_id == user_id).all()

    for order in orders:
        db.query(OrderItem).filter(
            OrderItem.order_id == order.id
        ).delete()

    # delete orders
    db.query(Order).filter(Order.user_id == user_id).delete()

    # delete cart
    db.query(Cart).filter(Cart.user_id == user_id).delete()

    # delete user
    user = db.query(User).filter(User.id == user_id).first()
    db.delete(user)

    db.commit()

    return {"message": "Account deleted"}