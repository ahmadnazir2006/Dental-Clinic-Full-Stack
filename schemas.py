from pydantic import BaseModel, ConfigDict, Field,model_validator
from datetime import date,time
from typing import Literal,Optional       
PatientStatus = Literal["active", "inactive", "archived"]
AppointmentStatus = Literal["booked", "completed", "cancelled", "updated"]
Userroles=Literal["admin", "doctor", "owner","pa"]
class PatientUpdate(BaseModel):
    name: str=Field(min_length=2, max_length=100)
    contact: str=Field(min_length=11, max_length=11,pattern=r"^03\d{9}$")
    medical_history: str=Field(min_length=1)
    address: str|None=Field(default=None, min_length=1, max_length=200)
    date_of_birth: date
    emergency_contact: str | None = Field(default=None, min_length=11, max_length=11,pattern=r"^03\d{9}$")
    patient_status: PatientStatus

class PatientCreate(BaseModel):
    name: str=Field(min_length=2, max_length=100)
    contact: str=Field(min_length=11, max_length=11,pattern=r"^03\d{9}$")
    medical_history: str=Field(min_length=1)
    address: str | None = Field(default=None, min_length=1, max_length=200)
    date_of_birth: date
    emergency_contact: str | None = Field(default=None, min_length=11, max_length=11,pattern=r"^03\d{9}$")
    patient_status: PatientStatus

class PatientResponse(BaseModel):
    patient_id: int
    name: str=Field(min_length=2, max_length=100)
    contact: str=Field(min_length=11, max_length=11,pattern=r"^03\d{9}$")
    medical_history: str=Field(min_length=1)
    address: str | None = Field(default=None, min_length=1, max_length=200)
    date_of_birth: date
    emergency_contact: str | None = Field(default=None, min_length=11, max_length=11,pattern=r"^03\d{9}$")   
    patient_status: PatientStatus

    model_config = ConfigDict(from_attributes=True)

class AppointmentCreate(BaseModel):
    patient_id: int
    user_id: int
    appointment_date: date
    appointment_time: time
    status: AppointmentStatus
    service_type: str | None = Field(default=None, min_length=1, max_length=100)
    fee: float | None = Field(default=None, ge=0)

    payment_method: Optional[Literal[
        "cash",
        "card",
        "bank_transfer",
        "online"
    ]] = None
    dues: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_dues(self):
        if self.fee is not None and self.dues is not None:
            if self.dues > self.fee:
                raise ValueError("Dues cannot be greater than fee")
        return self

class AppointmentResponse(BaseModel):
    appointment_id: int
    patient_id: int
    user_id: int
    appointment_date: date
    appointment_time: time
    status: AppointmentStatus
    service_type: str | None = Field(default=None, min_length=1, max_length=100)
    fee: float | None = Field(default=None, ge=0)
    payment_method: Optional[Literal[
        "cash",
        "card",
        "bank_transfer",
        "online"
    ]] = None
    dues: float | None = Field(default=None, ge=0)

    model_config = ConfigDict(from_attributes=True)
class AppointmentUpdate(BaseModel):
    appointment_date: date
    appointment_time: time
    status: AppointmentStatus
    service_type: str | None = Field(default=None, min_length=1, max_length=100)
    fee: float | None = Field(default=None, ge=0)
    payment_method: Optional[Literal[
        "cash",
        "card",
        "bank_transfer",
        "online"
    ]] = None
    dues: float | None = Field(default=None, ge=0)
    @model_validator(mode="after")
    def validate_dues(self):
        if self.fee is not None and self.dues is not None:
            if self.dues > self.fee:
                raise ValueError("Dues cannot be greater than fee")
        return self

class UserCreate(BaseModel):
    name: str=Field(min_length=2, max_length=100)
    email: str=Field(min_length=5, max_length=100)
    contact: str=Field(min_length=11, max_length=11,pattern=r"^03\d{9}$")
    password: str=Field(min_length=6)
    role:  Userroles

class UserResponse(BaseModel):
    user_id: int
    name: str=Field(min_length=2, max_length=100)
    email: str=Field(min_length=5, max_length=100)
    contact: str=Field(min_length=11, max_length=11,pattern=r"^03\d{9}$")
    role:  Userroles

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    name: str=Field(min_length=2, max_length=100)
    email: str=Field(min_length=5, max_length=100)
    contact: str=Field(min_length=11, max_length=11,pattern=r"^03\d{9}$")
    password: str=Field(min_length=6)
    role:  Userroles


class LoginRequest(BaseModel):
    email: str
    password: str




######Relationship Schemas
class AppointmentDetailResponse(BaseModel):
    appointment_id: int

    patient_id: int
    patient_name: str

    user_id: int
    user_name: str

    appointment_date: date
    appointment_time: time
    status: AppointmentStatus

    service_type: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    fee: float | None = Field(
        default=None,
        ge=0
    )

    payment_method: str | None = Field(
        default=None,
        min_length=1,
        max_length=50
    )

    dues: float | None = Field(
        default=None,
        ge=0
    )