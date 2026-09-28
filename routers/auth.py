
from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models import Appointment, Patient, User
from schemas import LoginRequest, UserCreate,UserResponse,UserUpdate
from dependencies import require_role
from sqlalchemy.exc import SQLAlchemyError
from security import hash_password, verify_password, create_access_token

router=APIRouter(tags=["Authentication"])


#login endpoint
@router.post("/login")
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user=db.query(User).filter(User.email==login_data.email).first()
    if not user:
        raise HTTPException(
        status_code=401,
        detail="Invalid email or password"
    )

    if not verify_password(login_data.password, user.password):
        raise HTTPException(
        status_code=401,
        detail="Invalid email or password"
    )
    access_token = create_access_token(
        data={
            "user_id": user.user_id,
            "role": user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }