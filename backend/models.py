from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Patient(Base):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    phone = Column(String(50), nullable=True)
    metadata = Column(JSON, default={})

class Appointment(Base):
    __tablename__ = 'appointments'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, nullable=False)
    scheduled_at = Column(DateTime, nullable=False)
    notes = Column(Text, default='')
    created_at = Column(DateTime, default=datetime.utcnow)

class Prescription(Base):
    __tablename__ = 'prescriptions'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, nullable=False)
    medication = Column(String(300))
    instructions = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class MessageMemory(Base):
    __tablename__ = 'message_memory'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, nullable=False)
    role = Column(String(50))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
