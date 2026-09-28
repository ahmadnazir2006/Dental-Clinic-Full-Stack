from sqlalchemy import Column, ForeignKey, Integer, String, Text, Date, Numeric, Time
from sqlalchemy.orm import relationship

from database import Base


class Patient(Base):
    __tablename__ = "patient"

    patient_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    contact = Column(String, nullable=False)
    medical_history = Column(Text, nullable=False)
    address = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=False)
    emergency_contact = Column(String, nullable=True)
    patient_status = Column(String, nullable=False)

    appointments = relationship(
        "Appointment",
        back_populates="patient"
    )


class Appointment(Base):
    __tablename__ = "appointment"

    appointment_id = Column(Integer, primary_key=True)
    patient_id = Column(
        Integer,
        ForeignKey("patient.patient_id"),
        nullable=False
    )
    user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )
    appointment_date = Column(Date, nullable=False)
    appointment_time = Column(Time, nullable=False)
    status = Column(String, nullable=False)
    service_type = Column(String, nullable=True)
    fee = Column(Numeric(10, 2), nullable=True)
    payment_method = Column(String, nullable=True)
    dues = Column(Numeric(10, 2), nullable=True)

    patient = relationship(
        "Patient",
        back_populates="appointments"
    )

    user = relationship(
        "User",
        back_populates="appointments"
    )


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    contact = Column(String, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)

    appointments = relationship(
        "Appointment",
        back_populates="user"
    )