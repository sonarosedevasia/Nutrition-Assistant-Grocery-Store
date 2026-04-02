import os
import re
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4

from backend.database_connection import get_db
from backend.category_model import Category

router = APIRouter(prefix="/admin/categories", tags=["Admin Categories"])

UPLOAD_DIR = "backend/uploads/categories"
PUBLIC_DIR = "uploads/categories"  # <-- PUBLIC PATH
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ---------------- ADD CATEGORY ----------------
@router.post("/add")
def add_category(
    name: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    existing = db.query(Category).filter(Category.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")

    original_name = image.filename.rsplit(".", 1)[0]
    safe_name = re.sub(r"[^a-zA-Z0-9_-]", "", original_name).lower()

    ext = image.filename.split(".")[-1]
    filename = f"{safe_name}-{uuid4().hex[:8]}.{ext}"

    disk_path = os.path.join(UPLOAD_DIR, filename)
    public_path = f"{PUBLIC_DIR}/{filename}"

    with open(disk_path, "wb") as f:
        f.write(image.file.read())

    category = Category(
        name=name,
        image_path=public_path  # ✅ FIXED
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return {"message": "Category added successfully"}


# ---------------- LIST CATEGORIES ----------------
@router.get("/list")
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()


# ---------------- UPDATE CATEGORY ----------------
@router.put("/{category_id}")
def update_category(
    category_id: int,
    name: str = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if name and name != category.name:
        duplicate = db.query(Category).filter(Category.name == name).first()
        if duplicate:
            raise HTTPException(status_code=400, detail="Category name already exists")
        category.name = name

    if image:
        # delete old image
        if category.image_path:
            old_file = os.path.join("backend", category.image_path)
            if os.path.exists(old_file):
                os.remove(old_file)

        original_name = image.filename.rsplit(".", 1)[0]
        safe_name = re.sub(r"[^a-zA-Z0-9_-]", "", original_name).lower()

        ext = image.filename.split(".")[-1]
        filename = f"{safe_name}-{uuid4().hex[:8]}.{ext}"

        disk_path = os.path.join(UPLOAD_DIR, filename)
        public_path = f"{PUBLIC_DIR}/{filename}"

        with open(disk_path, "wb") as f:
            f.write(image.file.read())

        category.image_path = public_path  # ✅ FIXED

    db.commit()
    db.refresh(category)

    return {"message": "Category updated successfully"}


# ---------------- DELETE CATEGORY ----------------
@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if category.image_path:
        file_to_delete = os.path.join("backend", category.image_path)
        if os.path.exists(file_to_delete):
            os.remove(file_to_delete)

    db.delete(category)
    db.commit()

    return {"message": "Category deleted successfully"}
