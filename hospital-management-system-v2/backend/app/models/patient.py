from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, Text
from sqlalchemy.orm import relationship
from app.database.db import db

class Patient(db.Model):
    """Patient model for storing patient information."""
    
    __tablename__ = 'patients'
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(10))
    address = Column(String(200))
    phone_number = Column(String(20))
    email = Column(String(120))
    emergency_contact = Column(String(120))
    blood_type = Column(String(5))
    allergies = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    appointments = relationship('Appointment', back_populates='patient')
    prescriptions = relationship('Prescription', back_populates='patient')
    bills = relationship('Bill', back_populates='patient')
    
    @property
    def full_name(self):
        """Return the patient's full name."""
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<Patient {self.full_name}>'
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'address': self.address,
            'phone_number': self.phone_number,
            'email': self.email,
            'emergency_contact': self.emergency_contact,
            'blood_type': self.blood_type,
            'allergies': self.allergies,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }