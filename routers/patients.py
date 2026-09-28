from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session

from database import get_db
from models import Patient, User
from schemas import PatientCreate, PatientResponse,PatientUpdate
from dependencies import require_role
from sqlalchemy.exc import SQLAlchemyError


router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


@router.get(
    "",
    response_model=list[PatientResponse]
)
def get_patients(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("doctor", "pa", "owner", "admin")
    )
):
    patients = db.query(Patient).all()
    return patients


@router.get(
    "/{patient_id}",
    response_model=PatientResponse
)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("doctor", "pa", "owner", "admin")
    )
):
    patient = db.query(Patient).filter(
        Patient.patient_id == patient_id
    ).first()

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return patient

@router.post("/patients", response_model=PatientResponse,status_code=status.HTTP_201_CREATED)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role("doctor", "pa", "admin"))):
    existing_patient=db.query(Patient).filter(
        Patient.contact==patient.contact
    ).first()

    if existing_patient:
        raise HTTPException(status_code=400, detail="Patient with this contact already exists")

    new_patient = Patient(
        name=patient.name,
        contact=patient.contact,
        medical_history=patient.medical_history,
        address=patient.address,
        date_of_birth=patient.date_of_birth,
        emergency_contact=patient.emergency_contact,
        patient_status=patient.patient_status
    )


    try:
        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred")

    return new_patient

@router.put("/patients/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: int,
    patient_data: PatientUpdate,
    db: Session = Depends(get_db), current_user: User = Depends(require_role("doctor", "pa", "admin"))):

    patient = db.query(Patient).filter(
            Patient.patient_id == patient_id
        ).first()
    
    if patient is None:
            raise HTTPException(
                status_code=404,
                detail="Patient not found"
            )
    
    existing_patient = db.query(Patient).filter(
        Patient.contact == patient_data.contact,
        Patient.patient_id != patient_id
    ).first()

    if existing_patient:
        raise HTTPException(
            status_code=400,
            detail="A patient with this contact number already exists"
        )
    

    patient.name = patient_data.name
    patient.contact = patient_data.contact
    patient.medical_history = patient_data.medical_history
    patient.address = patient_data.address
    patient.date_of_birth = patient_data.date_of_birth
    patient.emergency_contact = patient_data.emergency_contact
    patient.patient_status = patient_data.patient_status

    try:
        db.commit()
        db.refresh(patient)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred")

    return patient


@router.delete("/patients/{patient_id}",
            status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(patient_id:int,db: Session=Depends(get_db), current_user: User = Depends(require_role("admin"))):
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()

    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    db.delete(patient)
    db.commit()

