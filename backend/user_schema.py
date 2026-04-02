from pydantic import BaseModel, EmailStr, field_validator
import re

# -------------------------------
# Register Schema
# -------------------------------

class RegisterUserRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: str

    # ✅ Name validation
    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not re.fullmatch(r"[A-Za-z_ ]+", v):
            raise ValueError("Name can contain only letters and underscore")
        return v

    # ✅ Phone validation (exactly 10 digits)
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if not re.fullmatch(r"\d{10}", v):
            raise ValueError("Phone number must be exactly 10 digits")
        return v

    # ✅ Password validation (minimum 6 characters)
    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


# -------------------------------
# Login Schema
# -------------------------------

class LoginUserRequest(BaseModel):
    email: EmailStr
    password: str


# -------------------------------
# Forgot Password Schema
# -------------------------------

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


# -------------------------------
# Reset Password Schema
# -------------------------------

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    new_password: str

    # ✅ Apply same password rule for reset
    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v