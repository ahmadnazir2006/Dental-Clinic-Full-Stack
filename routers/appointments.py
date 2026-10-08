from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

from database import get_db
from models import Appointment, Patient, User
from schemas import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentUpdate,
    AppointmentDetailResponse
)
from dependencies import require_role


router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)


# =========================
# GET ALL APPOINTMENTS
# =========================

@router.get(
    "/",
    response_model=list[AppointmentResponse]
)
def get_appointments(
    status: str | None = None,
    patient_id: int | None = None,
    user_id: int | None = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("doctor", "pa", "owner", "admin")
    )
):
    if skip < 0:
        raise HTTPException(
            status_code=400,
            detail="Skip cannot be negative"
        )

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 100"
        )

    query = db.query(Appointment)

    if status:
        query = query.filter(
            Appointment.status == status
        )

    if patient_id:
        query = query.filter(
            Appointment.patient_id == patient_id
        )

    if user_id:
        query = query.filter(
            Appointment.user_id == user_id
        )

    appointments = query.offset(skip).limit(limit).all()

    return appointments


# =========================
# GET PATIENT APPOINTMENTS
# =========================

@router.get(
    "/patient/{patient_id}",
    response_model=list[AppointmentResponse]
)
def get_patient_appointments(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("doctor", "pa", "owner", "admin")
    )
):
    patient = db.query(Patient).filter(
        Patient.patient_id == patient_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    appointments = db.query(Appointment).filter(
        Appointment.patient_id == patient_id
    ).all()

    return appointments


# =========================
# GET DOCTOR APPOINTMENTS
# =========================

@router.get(
    "/doctor/{user_id}",
    response_model=list[AppointmentResponse]
)
def get_doctor_appointments(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("doctor", "pa", "owner", "admin")
    )
):
    user = db.query(User).filter(
        User.user_id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.role not in ["doctor", "pa"]:
        raise HTTPException(
            status_code=400,
            detail="Appointments can only belong to doctors or PAs"
        )

    appointments = db.query(Appointment).filter(
        Appointment.user_id == user_id
    ).all()

    return appointments
# =========================
# GET SINGLE APPOINTMENT
# =========================

@router.get(
    "/{appointment_id}",
    response_model=AppointmentDetailResponse
)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("doctor", "pa", "owner", "admin")
    )
):
    appointment = db.query(Appointment).filter(
        Appointment.appointment_id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    return {
        "appointment_id": appointment.appointment_id,

        "patient_id": appointment.patient_id,
        "patient_name": appointment.patient.name,

        "user_id": appointment.user_id,
        "user_name": appointment.user.name,

        "appointment_date": appointment.appointment_date,
        "appointment_time": appointment.appointment_time,
        "status": appointment.status,

        "service_type": appointment.service_type,
        "fee": appointment.fee,
        "payment_method": appointment.payment_method,
        "dues": appointment.dues
    }


# =========================
# UPDATE APPOINTMENT
# =========================

@router.put(
    "/{appointment_id}",
    response_model=AppointmentUpdate
)
def update_appointment(
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("doctor", "pa", "admin")
    )
):
    appointment = db.query(Appointment).filter(
        Appointment.appointment_id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    if appointment.status == "completed":
        raise HTTPException(
            status_code=400,
            detail="Completed appointments cannot be changed"
        )

    if appointment.status == "cancelled":
        raise HTTPException(
            status_code=400,
            detail="Cancelled appointments cannot be changed"
        )

    appointment_datetime = datetime.combine(
        appointment_data.appointment_date,
        appointment_data.appointment_time
    )

    if appointment_datetime < datetime.now():
        raise HTTPException(
            status_code=400,
            detail="Appointment date and time cannot be in the past"
        )

    existing_user_appointment = db.query(Appointment).filter(
        Appointment.user_id == appointment.user_id,
        Appointment.appointment_date == appointment_data.appointment_date,
        Appointment.appointment_time == appointment_data.appointment_time,
        Appointment.appointment_id != appointment_id
    ).first()

    if existing_user_appointment:
        raise HTTPException(
            status_code=400,
            detail="User already has an appointment at the specified date and time"
        )

    existing_patient_appointment = db.query(Appointment).filter(
        Appointment.patient_id == appointment.patient_id,
        Appointment.appointment_date == appointment_data.appointment_date,
        Appointment.appointment_time == appointment_data.appointment_time,
        Appointment.appointment_id != appointment_id
    ).first()

    if existing_patient_appointment:
        raise HTTPException(
            status_code=400,
            detail="Patient already has an appointment at the specified date and time"
        )

    appointment.appointment_date = appointment_data.appointment_date
    appointment.appointment_time = appointment_data.appointment_time
    appointment.status = appointment_data.status
    appointment.service_type = appointment_data.service_type
    appointment.fee = appointment_data.fee
    appointment.payment_method = appointment_data.payment_method
    appointment.dues = appointment_data.dues

    try:
        db.commit()
        db.refresh(appointment)
        return appointment

    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Database error occurred"
        )


# =========================
# CREATE APPOINTMENT
# =========================

@router.post(
    "/",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("doctor", "pa", "admin")
    )
):
    existing_patient = db.query(Patient).filter(
        Patient.patient_id == appointment.patient_id,
        Patient.patient_status == "active"
    ).first()

    if not existing_patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    existing_user = db.query(User).filter(
        User.user_id == appointment.user_id
    ).first()

    if not existing_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if existing_user.role not in ["doctor", "pa"]:
        raise HTTPException(
            status_code=400,
            detail="Appointments can only be assigned by doctors or PAs"
        )

    appointment_datetime = datetime.combine(
        appointment.appointment_date,
        appointment.appointment_time
    )

    if appointment_datetime < datetime.now():
        raise HTTPException(
            status_code=400,
            detail="Appointment date and time cannot be in the past"
        )

    existing_appointment = db.query(Appointment).filter(
        Appointment.patient_id == appointment.patient_id,
        Appointment.appointment_date == appointment.appointment_date,
        Appointment.appointment_time == appointment.appointment_time
    ).first()

    if existing_appointment:
        raise HTTPException(
            status_code=400,
            detail="Appointment already exists for the specified date and time"
        )

    existing_user_appointment = db.query(Appointment).filter(
        Appointment.user_id == appointment.user_id,
        Appointment.appointment_date == appointment.appointment_date,
        Appointment.appointment_time == appointment.appointment_time
    ).first()

    if existing_user_appointment:
        raise HTTPException(
            status_code=400,
            detail="User already has an appointment at the specified date and time"
        )

    new_appointment = Appointment(
        patient_id=appointment.patient_id,
        user_id=appointment.user_id,
        appointment_date=appointment.appointment_date,
        appointment_time=appointment.appointment_time,
        status=appointment.status,
        service_type=appointment.service_type,
        fee=appointment.fee,
        payment_method=appointment.payment_method,
        dues=appointment.dues
    )

    try:
        db.add(new_appointment)
        db.commit()
        db.refresh(new_appointment)

        return new_appointment

    except SQLAlchemyError as e:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================
# DELETE APPOINTMENT
# =========================

@router.delete(
    "/{appointment_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("admin")
    )
):
    appointment = db.query(Appointment).filter(
        Appointment.appointment_id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    try:
        db.delete(appointment)
        db.commit()

    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Database error occurred"
        )