

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database_connection import get_db
from backend.jwt_utils import get_current_user
from backend.cart_model import Cart
from backend.product_model import Product
from backend.order_model import Order, OrderItem

router = APIRouter(prefix="/orders", tags=["Orders"])

from sqlalchemy import func

# ===============================
# GET TOP SELLING PRODUCTS
# ===============================
@router.get("/top-selling")
def get_top_selling_products(db: Session = Depends(get_db)):

    results = (
        db.query(
            OrderItem.product_id,
            func.sum(OrderItem.quantity).label("total_sold")
        )
        .group_by(OrderItem.product_id)
        .having(func.sum(OrderItem.quantity) >= 2)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(4)
        .all()
    )

    products = []

    for row in results:
        product = db.query(Product).filter(Product.id == row.product_id).first()

        if product:
            products.append({
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "package_size": product.package_size,
                "unit": product.unit,
                "image_path": product.image_path
            })

    # fallback
    if len(products) < 4:

        existing_ids = [p["id"] for p in products]

        fallback_products = (
            db.query(Product)
            .filter(~Product.id.in_(existing_ids))
            .limit(4 - len(products))
            .all()
        )

        for product in fallback_products:
            products.append({
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "package_size": product.package_size,
                "unit": product.unit,
                "image_path": product.image_path
            })

    return products
# -------------------------------
# CREATE ORDER
# -------------------------------
@router.post("/create")
def create_order(
    delivery_name: str,
    delivery_phone: str,
    delivery_address: str,
    delivery_city: str,
    delivery_pincode: str,
    payment_method: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    # Validate payment method
    if payment_method not in ["cod", "upi"]:
        raise HTTPException(status_code=400, detail="Invalid payment method")

    # Get user's cart
    cart_items = db.query(Cart).filter(
        Cart.user_id == current_user["id"]
    ).all()

    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total_amount = 0

    # First pass: validate stock + calculate total
    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for {product.name}"
            )

        total_amount += product.price * item.quantity
            # Calculate tax (10%)
    tax = total_amount * 0.10
    final_total = total_amount + tax
    # Create Order
    new_order = Order(
        user_id=current_user["id"],
        total_amount=final_total,
        payment_method=payment_method,
        payment_status="paid" if payment_method == "upi" else "pending",
        order_status="placed",
        delivery_name=delivery_name,
        delivery_phone=delivery_phone,
        delivery_address=delivery_address,
        delivery_city=delivery_city,
        delivery_pincode=delivery_pincode
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # Create Order Items + Reduce Stock
    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()

        order_item = OrderItem(
            order_id=new_order.id,
            product_id=product.id,
            quantity=item.quantity,
            price_at_purchase=product.price
        )

        db.add(order_item)

        # Reduce stock
        product.stock -= item.quantity

    # Clear cart
    db.query(Cart).filter(
        Cart.user_id == current_user["id"]
    ).delete()

    db.commit()

    return {
        "message": "Order placed successfully",
        "order_id": new_order.id
    }
# ===============================
# GET MY ORDERS (WITH DATE + STATUS)
# ===============================
@router.get("/my")
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    orders = db.query(Order).filter(
        Order.user_id == current_user["id"]
    ).order_by(Order.created_at.desc()).all()

    return [
        {
            "id": order.id,
            "total_amount": order.total_amount,
            "created_at": order.created_at,
            "order_status": order.order_status
        }
        for order in orders
    ]
# ===============================
# GET ORDER ITEMS (FOR COLLAPSIBLE)
# ===============================
@router.get("/{order_id}/items")
def get_order_items(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user["id"]
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return [
        {
            "product_name": item.product.name,
            "quantity": item.quantity
        }
        for item in order.items
    ]
    # -------------------------------
# GET ORDER DETAILS
# -------------------------------
@router.get("/{order_id}")
def get_order_details(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user["id"]
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order_items = db.query(OrderItem).filter(
        OrderItem.order_id == order_id
    ).all()

    items_data = []

    for item in order_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        items_data.append({
            "product_name": product.name if product else "Unknown",
            "quantity": item.quantity,
            "price": item.price_at_purchase,
            "total": item.price_at_purchase * item.quantity,
            "image": product.image_path if product else None
        })

    return {
        "id": order.id,
        "delivery_name": order.delivery_name,
        "delivery_phone": order.delivery_phone,
        "delivery_address": order.delivery_address,
        "delivery_city": order.delivery_city,
        "delivery_pincode": order.delivery_pincode,
        "total_amount": order.total_amount,
        "items": items_data
    }
# ===============================
# ADMIN - GET ALL ORDERS
# ===============================
@router.get("/admin/all")
def get_all_orders(db: Session = Depends(get_db)):

    orders = db.query(Order).order_by(Order.created_at.desc()).all()

    result = []

    for order in orders:

        items_count = db.query(
        func.sum(OrderItem.quantity)
        ).filter(
        OrderItem.order_id == order.id
        ).scalar() or 0

        result.append({
            "id": order.id,
            "customer_name": order.delivery_name,
            "phone": order.delivery_phone,
            "date": order.created_at,
            "total": order.total_amount,
            "status": order.order_status,
            "payment_method": order.payment_method,
            "payment_status": order.payment_status,
            "items_count": items_count
        })

    return result
# ===============================
# ADMIN - ORDER DETAILS
# ===============================
@router.get("/admin/{order_id}")
def admin_order_details(order_id: int, db: Session = Depends(get_db)):

    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order_items = db.query(OrderItem).filter(
        OrderItem.order_id == order_id
    ).all()

    items_data = []

    for item in order_items:

        product = db.query(Product).filter(
            Product.id == item.product_id
        ).first()

        items_data.append({
            "name": product.name if product else "Unknown",
            "image": product.image_path if product else None,
            "quantity": item.quantity,
            "price": item.price_at_purchase,
            "subtotal": item.price_at_purchase * item.quantity
        })

    return {
        "order_id": order.id,
        "customer_name": order.delivery_name,
        "phone": order.delivery_phone,
        "address": order.delivery_address,
        "city": order.delivery_city,
        "pincode": order.delivery_pincode,
        "date": order.created_at,
        "payment_method": order.payment_method,
        "payment_status": order.payment_status,
        "status": order.order_status,
        "total": order.total_amount,
        "items": items_data
    }
# ===============================
# ADMIN - UPDATE ORDER STATUS
# ===============================
@router.put("/admin/{order_id}/status")
def update_order_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db)
):

    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    allowed = ["placed","packed","delivered","cancelled"]

    if status not in allowed:
        raise HTTPException(status_code=400, detail="Invalid status")

    order.order_status = status

    # ⭐ IMPORTANT FIX
    if status == "delivered" and order.payment_method == "cod":
        order.payment_status = "paid"

    db.commit()

    return {"message":"Order status updated"}