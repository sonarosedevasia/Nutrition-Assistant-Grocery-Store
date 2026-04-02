from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.jwt_utils import create_access_token
from backend.database_connection import get_db
from backend.user_model import User
from fastapi.security import OAuth2PasswordRequestForm
from backend.jwt_utils import create_access_token
from backend.user_schema import (
    RegisterUserRequest,
    LoginUserRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from backend.password_utils import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])

# -------------------------------
# REGISTER
# -------------------------------

@router.post("/register")
def register_user(request: RegisterUserRequest, db: Session = Depends(get_db)):
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed_pwd = hash_password(request.password)

    # Create user
    new_user = User(
        name=request.name,
        email=request.email,
        phone=request.phone,
        hashed_password=hashed_pwd,
        role="user"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}


# -------------------------------
# LOGIN
# -------------------------------

@router.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    access_token = create_access_token(
        data={
            "id": user.id,
            "role": user.role,
            "name":user.name
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_name": user.name,
        "role": user.role
    }

# -------------------------------
# FORGOT PASSWORD (SIMPLIFIED)
# -------------------------------

@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="Email not found")

    return {"message": "Email verified. Proceed to reset password."}


# -------------------------------
# RESET PASSWORD
# -------------------------------

@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = hash_password(request.new_password)
    db.commit()

    return {"message": "Password updated successfully"}
from backend.jwt_utils import get_current_user


# -------------------------------
# GET CURRENT USER DETAILS
# -------------------------------
@router.get("/me")
def get_current_user_details(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == current_user["id"]).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "name": user.name,
        "email": user.email,
        "phone": user.phone
    }