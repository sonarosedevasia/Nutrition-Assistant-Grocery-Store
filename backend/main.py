from fastapi import FastAPI

from backend.database_connection import engine, Base
from backend.user_model import User
from backend.auth_routes import router as auth_router
from backend.category_routes import router as category_router
from backend.category_model import Category
from fastapi.staticfiles import StaticFiles
from backend.product_routes import router as product_router
from backend import cart_model
from backend.cart_routes import router as cart_router
from backend import order_model
from backend.order_routes import router as order_router
from backend.user_routes import router as user_router
from backend.admin_routes import router as admin_router
from backend.feedback_routes import router as feedback_router
app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware
app.mount("/uploads", StaticFiles(directory="backend/uploads"), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # for development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)
app.include_router(category_router)

# Include authentication routes
app.include_router(auth_router)
app.include_router(product_router)
app.include_router(cart_router)
app.include_router(order_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(feedback_router)
@app.get("/")
def read_root():
    return {"message": "Backend is running"}
