from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.db import db

class Bill(db.Model):
    """Bill model for managing patient billing and payments."""
    
    __tablename__ = 'bills'
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False, index=True)
    appointment_id = Column(Integer, ForeignKey('appointments.id'), nullable=True)
    prescription_id = Column(Integer, ForeignKey('prescriptions.id'), nullable=True)
    amount = Column(Float, nullable=False)
    status = Column(String(20), default='unpaid', index=True)  # unpaid, paid, partially_paid
    payment_method = Column(String(50))  # cash, credit_card, insurance, etc.
    payment_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship('Patient', back_populates='bills')
    appointment = relationship('Appointment', back_populates='bills')
    prescription = relationship('Prescription', back_populates='bills')
    
    @property
    def is_paid(self):
        """Check if the bill is fully paid."""
        return self.status == 'paid'
    
    @property
    def due_amount(self):
        """Calculate the remaining amount due."""
        if self.status == 'paid':
            return 0.0
        elif self.status == 'partially_paid':
            # In a real system, you would track partial payments
            return self.amount * 0.5  # Example: 50% remaining
        return self.amount
    
    def __repr__(self):
        return f'<Bill {self.id} - Patient: {self.patient.full_name}, Amount: ${self.amount}>'
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': self.patient.full_name if self.patient else None,
            'appointment_id': self.appointment_id,
            'prescription_id': self.prescription_id,
            'amount': float(self.amount),
            'status': self.status,
            'payment_method': self.payment_method,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'due_amount': float(self.due_amount),
            'is_paid': self.is_paid,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }