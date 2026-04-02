from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database_connection import get_db
from backend.cart_model import Cart
from backend.product_model import Product
from backend.jwt_utils import get_current_user
from backend.category_model import Category

router = APIRouter(prefix="/cart", tags=["Cart"])


# -------------------------------
# ADD TO CART
# -------------------------------
@router.post("/add/{product_id}")
def add_to_cart(
    product_id: int,
    quantity: int = 1,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Check if product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check if already in cart
    existing_item = db.query(Cart).filter(
        Cart.user_id == current_user["id"],
        Cart.product_id == product_id
    ).first()

    if existing_item:
        existing_item.quantity += quantity
    else:
        cart_item = Cart(
            user_id=current_user["id"],
            product_id=product_id,
            quantity=quantity
        )
        db.add(cart_item)

    db.commit()
    return {"message": "Product added to cart"}


# -------------------------------
# GET MY CART
# -------------------------------
@router.get("/my")
def get_my_cart(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cart_items = db.query(Cart).filter(
        Cart.user_id == current_user["id"]
    ).all()

    result = []

    for item in cart_items:

        product = db.query(Product).filter(
            Product.id == item.product_id
        ).first()

        category = db.query(Category).filter(
            Category.id == product.category_id
        ).first()

        result.append({
            "cart_id": item.id,
            "product_id": product.id,
            "product_name": product.name,
            "price": product.price,
            "quantity": item.quantity,
            "total": product.price * item.quantity,
            "image_path": product.image_path,
            "category_name": category.name if category else None,
            "nutrient_type":product.nutrient_type
        })

    return result

# -------------------------------
# REMOVE FROM CART
# -------------------------------
@router.delete("/remove/{cart_id}")
def remove_from_cart(
    cart_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cart_item = db.query(Cart).filter(
        Cart.id == cart_id,
        Cart.user_id == current_user["id"]
    ).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    db.delete(cart_item)
    db.commit()

    return {"message": "Item removed from cart"}