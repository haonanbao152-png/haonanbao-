from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, Time, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database.db import db

class Appointment(db.Model):
    """Appointment model for managing patient appointments."""
    
    __tablename__ = 'appointments'
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    appointment_type = Column(String(50), nullable=False)
    date = Column(Date, nullable=False, index=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    status = Column(String(20), default='scheduled', index=True)  # scheduled, completed, cancelled, no_show
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship('Patient', back_populates='appointments')
    doctor = relationship('User', back_populates='appointments')
    prescriptions = relationship('Prescription', back_populates='appointment')
    bills = relationship('Bill', back_populates='appointment')
    
    def __repr__(self):
        return f'<Appointment {self.id} - {self.patient.full_name} with Dr. {self.doctor.full_name}>'
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': self.patient.full_name if self.patient else None,
            'doctor_id': self.doctor_id,
            'doctor_name': self.doctor.full_name if self.doctor else None,
            'appointment_type': self.appointment_type,
            'date': self.date.isoformat() if self.date else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }