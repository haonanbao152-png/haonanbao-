from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database.db import db

class Prescription(db.Model):
    """Prescription model for managing medical prescriptions."""
    
    __tablename__ = 'prescriptions'
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    appointment_id = Column(Integer, ForeignKey('appointments.id'), nullable=True)
    diagnosis = Column(Text, nullable=False)
    notes = Column(Text)
    status = Column(String(20), default='active', index=True)  # active, filled, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship('Patient', back_populates='prescriptions')
    doctor = relationship('User', back_populates='prescriptions')
    appointment = relationship('Appointment', back_populates='prescriptions')
    items = relationship('PrescriptionItem', back_populates='prescription', cascade='all, delete-orphan')
    bills = relationship('Bill', back_populates='prescription')
    
    @property
    def total_items(self):
        """Return the total number of medication items in this prescription."""
        return len(self.items)
    
    def __repr__(self):
        return f'<Prescription {self.id} - Patient: {self.patient.full_name}>'
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': self.patient.full_name if self.patient else None,
            'doctor_id': self.doctor_id,
            'doctor_name': self.doctor.full_name if self.doctor else None,
            'appointment_id': self.appointment_id,
            'diagnosis': self.diagnosis,
            'notes': self.notes,
            'status': self.status,
            'total_items': self.total_items,
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class PrescriptionItem(db.Model):
    """Prescription Item model for individual medication items in a prescription."""
    
    __tablename__ = 'prescription_items'
    
    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(Integer, ForeignKey('prescriptions.id'), nullable=False, index=True)
    medication_id = Column(Integer, ForeignKey('medications.id'), nullable=False, index=True)
    dosage = Column(String(100), nullable=False)  # e.g., "5mg", "10mL"
    frequency = Column(String(100), nullable=False)  # e.g., "twice daily", "every 8 hours"
    duration = Column(String(100), nullable=False)  # e.g., "for 7 days", "for 1 month"
    notes = Column(Text)
    
    # Relationships
    prescription = relationship('Prescription', back_populates='items')
    medication = relationship('Medication', back_populates='prescription_items')
    
    def __repr__(self):
        return f'<PrescriptionItem {self.id} - {self.medication.name}>'
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'prescription_id': self.prescription_id,
            'medication_id': self.medication_id,
            'medication_name': self.medication.name if self.medication else None,
            'medication_strength': self.medication.strength if self.medication else None,
            'dosage': self.dosage,
            'frequency': self.frequency,
            'duration': self.duration,
            'notes': self.notes,
            'unit_price': float(self.medication.unit_price) if self.medication else 0.0
        }