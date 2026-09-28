from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models import Appointment, Patient, User
from schemas import LoginRequest, UserCreate,UserResponse,UserUpdate
from dependencies import require_role
from sqlalchemy.exc import SQLAlchemyError
from security import hash_password, verify_password, create_access_token

router=APIRouter(prefix="/users",tags=["Users"])


#User endpoints can be added here in a similar manner, following the same structure as the patient endpoints.

@router.get("/users",response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db), current_user: User = Depends(require_role("admin","owner"))):
    
    users = db.query(User).all()
    return users
    



@router.get("/users/{user_id}",response_model=UserResponse)
def get_user(user_id:int,db: Session = Depends(get_db), current_user: User = Depends(require_role("admin","owner"))):
    user=db.query(User).filter(User.user_id==user_id).first()
    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    return user

@router.put("/users/{user_id}",response_model=UserResponse)
def update_user(user_id:int,user_data:UserCreate,db: Session = Depends(get_db),current_user: User = Depends(require_role("admin","owner"))):
    user=db.query(User).filter(User.user_id==user_id).first()
    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    
    existing_user=db.query(User).filter(
        User.email==user_data.email,
        User.user_id!=user_id
    ).first()

    if existing_user:
        raise HTTPException(status_code=400,detail="A user with this email already exists")

    existing_contact=db.query(User).filter(
        User.contact==user_data.contact,
        User.user_id!=user_id
    ).first()

    if existing_contact:
        raise HTTPException(status_code=400,detail="A user with this contact already exists")

    hashed_password=hash_password(user_data.password)

    user.name=user_data.name
    user.email=user_data.email
    user.contact=user_data.contact
    user.password=hashed_password
    user.role=user_data.role

    try:
        db.commit()
        db.refresh(user)
        return user
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500,detail="Database error occurred")


@router.post("/users",response_model=UserResponse,status_code=status.HTTP_201_CREATED)
def create_user(user:UserCreate, db: Session = Depends(get_db),current_user: User = Depends(require_role("admin","owner"))):
    existing_user = (db.query(User).filter(User.email == user.email).first())
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    existing_contact = db.query(User).filter(
        User.contact == user.contact
    ).first()

    if existing_contact:
        raise HTTPException(
            status_code=400,
            detail="User with this contact already exists"
        )
    hashed_password = hash_password(user.password)

    new_user = User(
        name=user.name,
        email=user.email,
        contact=user.contact,
        password=hashed_password,
        role=user.role
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred")


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db),current_user: User = Depends(require_role("admin","owner"))):

    user = db.query(User).filter(
        User.user_id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    try:
        db.delete(user)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database error occurred"
        )




