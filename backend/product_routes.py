import os
import re
from uuid import uuid4

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from backend.jwt_utils import require_admin
from backend.database_connection import get_db
from backend.product_model import Product

router = APIRouter(prefix="/admin/products", tags=["Admin Products"])

UPLOAD_DIR = "backend/uploads/products"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ---------- ADD PRODUCT ----------
@router.post("/add")
def add_product(
    name: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    description: str = Form(...),
    package_size: float = Form(...),
    unit: str = Form(...),
    category_id: int = Form(...),
    nutrient_type: str = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):

    # clean filename
    base = re.sub(r"[^a-zA-Z0-9_-]", "", name.lower())
    ext = image.filename.split(".")[-1]
    filename = f"{base}-{uuid4().hex[:8]}.{ext}"

    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(image.file.read())

    product = Product(
    name=name,
    price=price,
    stock=stock,
    description=description,
    package_size=package_size,
    unit=unit,
    category_id=category_id,
    image_path=f"uploads/products/{filename}",
    nutrient_type=nutrient_type
)


    db.add(product)
    db.commit()
    db.refresh(product)

    return {"message": "Product added successfully"}


# ---------- LIST PRODUCTS ----------
from backend.category_model import Category

@router.get("/list")
def list_products(db: Session = Depends(get_db)):
    products = (
    db.query(
        Product.id,
        Product.name,
        Product.price,
        Product.stock,
        Product.description,
        Product.package_size,
        Product.unit,
        Product.image_path,
        Product.nutrient_type,
        Category.name.label("category_name"),
        Category.id.label("category_id")
    )
    .join(Category, Product.category_id == Category.id)
    .all()
)

    return [
    {
        "id": p.id,
        "name": p.name,
        "price": p.price,
        "stock": p.stock,
        "description": p.description,
        "package_size": p.package_size,   
        "unit": p.unit,                   
        "image_path": p.image_path,
        "nutrient_type": p.nutrient_type,
        "category_name": p.category_name,
        "category_id": p.category_id
    }
    for p in products
]



# ---------- DELETE PRODUCT ----------
@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if os.path.exists(product.image_path):
        os.remove(product.image_path)

    db.delete(product)
    db.commit()

    return {"message": "Product deleted"}

@router.put("/{product_id}")
def update_product(
    product_id: int,
    name: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    description: str = Form(...),
    package_size: float = Form(...),   
    unit: str = Form(...),             
    category_id: int = Form(...),
    nutrient_type: str = Form("none"),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):

    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # update fields
    product.name = name
    product.price = price
    product.stock = stock
    product.description = description  
    product.package_size = package_size
    product.unit = unit
    product.category_id = category_id
    product.nutrient_type = nutrient_type



    # update image only if new image selected
    if image:
        if os.path.exists(product.image_path):
            os.remove(product.image_path)

        base = re.sub(r"[^a-zA-Z0-9_-]", "", name.lower())
        ext = image.filename.split(".")[-1]
        filename = f"{base}-{uuid4().hex[:8]}.{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as f:
            f.write(image.file.read())

        product.image_path = f"uploads/products/{filename}"


    db.commit()
    return {"message": "Product updated successfully"}
# ---------- GET SINGLE PRODUCT ----------
@router.get("/{product_id}")
def get_single_product(product_id: int, db: Session = Depends(get_db)):

    product = (
        db.query(
            Product.id,
            Product.name,
            Product.price,
            Product.stock,
            Product.package_size,
            Product.unit,
            Product.image_path,
            Product.description,
            Category.name.label("category_name"),
            Category.id.label("category_id")
        )
        .join(Category, Product.category_id == Category.id)
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return {
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "stock": product.stock,
        "package_size": product.package_size,
        "unit": product.unit,
        "image_path": product.image_path,
        "description": product.description,
        "category_name": product.category_name,
        "category_id": product.category_id
    }
@router.get("/recommend/{nutrient}")
def recommend_products(nutrient: str, db: Session = Depends(get_db)):

    products = (
        db.query(Product)
        .filter(Product.nutrient_type == nutrient)
        .limit(3)
        .all()
    )

    return products