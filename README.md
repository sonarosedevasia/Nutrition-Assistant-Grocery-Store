Nutrition-Based Online Grocery Store

A full-stack grocery store web application built using FastAPI and HTML/CSS/JavaScript.
This system provides smart product recommendations based on nutritional balance.

Key Feature

Each product is assigned a nutrient type (Vitamin, Protein, Fiber, Calcium).
The system analyzes items in the cart, detects missing nutrients, and suggests products to maintain a balanced diet.

Features

* User Registration & Login (JWT Authentication)
* Browse Products & Categories
* Add to Cart 
* Nutrient-based Product Suggestions
* Checkout
* Admin Panel for Product & Order Management

Tech Stack

* Backend: FastAPI, SQLite
* Frontend: HTML, CSS, JavaScript

Setup

git clone <your-repo-link>
cd online_grocery_store_finalnew2

venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --reload

Run Frontend

Open:

frontend/login.html

 ccess

* Users can register directly in the application
* Password must be at least 6 characters (e.g., example@123)

Notes

* Backend must be running before using frontend
* `.gitignore` is used to exclude sensitive files
