from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database_connection import get_db
from backend.feedback_model import Feedback
from backend.jwt_utils import get_current_user

router = APIRouter(prefix="/feedback", tags=["Feedback"])


# Create feedback
@router.post("/create")
def create_feedback(
    rating: int,
    comment: str,
    order_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    feedback = Feedback(
        user_id=current_user["id"],
        order_id=order_id,
        rating=rating,
        comment=comment
    )

    db.add(feedback)
    db.commit()

    return {"message": "Feedback submitted"}


# ==============================
# ADMIN - GET ALL FEEDBACK
# ==============================

from backend.user_model import User

@router.get("/all")
def get_all_feedback(db: Session = Depends(get_db)):

    feedbacks = db.query(Feedback).all()

    result = []

    for f in feedbacks:

        user = db.query(User).filter(User.id == f.user_id).first()

        result.append({
            "user_name": user.name if user else "Unknown",
            "order_id": f.order_id,
            "rating": f.rating,
            "comment": f.comment,
            "created_at": f.created_at
        })

    return result