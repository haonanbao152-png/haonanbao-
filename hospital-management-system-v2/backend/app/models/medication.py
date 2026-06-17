from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import relationship
from app.database.db import db

class Medication(db.Model):
    """Medication model for managing pharmaceutical inventory."""
    
    __tablename__ = 'medications'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    dosage_form = Column(String(50))  # tablet, capsule, liquid, injection, etc.
    strength = Column(String(50))  # e.g., 5mg, 10mg/mL
    manufacturer = Column(String(100))
    stock_quantity = Column(Integer, default=0)
    unit_price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    prescription_items = relationship('PrescriptionItem', back_populates='medication')
    
    def __repr__(self):
        return f'<Medication {self.name} ({self.strength})>'
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'dosage_form': self.dosage_form,
            'strength': self.strength,
            'manufacturer': self.manufacturer,
            'stock_quantity': self.stock_quantity,
            'unit_price': float(self.unit_price),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }