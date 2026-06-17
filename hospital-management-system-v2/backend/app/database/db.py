from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()

# Import models to ensure they are registered with SQLAlchemy
from app.models.user import User
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.medication import Medication
from app.models.prescription import Prescription, PrescriptionItem
from app.models.bill import Bill