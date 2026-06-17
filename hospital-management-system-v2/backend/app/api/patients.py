from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database.db import db
from app.models.patient import Patient

bp = Blueprint('patients', __name__)

@bp.route('/', methods=['GET'])
@jwt_required()
def get_patients():
    """Get all patients with pagination and filtering."""
    current_user = get_jwt_identity()
    
    # Query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    
    # Base query
    query = Patient.query
    
    # Search functionality
    if search:
        search_term = f'%{search}%'
        query = query.filter(
            (Patient.first_name.ilike(search_term)) |
            (Patient.last_name.ilike(search_term)) |
            (Patient.phone_number.ilike(search_term)) |
            (Patient.email.ilike(search_term))
        )
    
    # Pagination
    pagination = query.order_by(Patient.last_name, Patient.first_name).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    patients = pagination.items
    total = pagination.total
    
    return jsonify({
        'patients': [patient.to_dict() for patient in patients],
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': pagination.pages
    }), 200

@bp.route('/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_patient(patient_id):
    """Get a specific patient by ID."""
    patient = Patient.query.get(patient_id)
    
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    
    return jsonify(patient.to_dict()), 200

@bp.route('/', methods=['POST'])
@jwt_required()
def create_patient():
    """Create a new patient."""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['first_name', 'last_name', 'date_of_birth', 'gender']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Create new patient
    new_patient = Patient(**data)
    
    try:
        db.session.add(new_patient)
        db.session.commit()
        return jsonify(new_patient.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/<int:patient_id>', methods=['PUT'])
@jwt_required()
def update_patient(patient_id):
    """Update an existing patient."""
    patient = Patient.query.get(patient_id)
    
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    
    data = request.get_json()
    
    # Update patient fields
    for key, value in data.items():
        if hasattr(patient, key):
            setattr(patient, key, value)
    
    try:
        db.session.commit()
        return jsonify(patient.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/<int:patient_id>', methods=['DELETE'])
@jwt_required()
def delete_patient(patient_id):
    """Delete a patient."""
    patient = Patient.query.get(patient_id)
    
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    
    try:
        db.session.delete(patient)
        db.session.commit()
        return jsonify({'message': 'Patient deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/<int:patient_id>/appointments', methods=['GET'])
@jwt_required()
def get_patient_appointments(patient_id):
    """Get all appointments for a specific patient."""
    patient = Patient.query.get(patient_id)
    
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    
    appointments = patient.appointments
    
    return jsonify({
        'appointments': [appointment.to_dict() for appointment in appointments],
        'total': len(appointments)
    }), 200

@bp.route('/<int:patient_id>/prescriptions', methods=['GET'])
@jwt_required()
def get_patient_prescriptions(patient_id):
    """Get all prescriptions for a specific patient."""
    patient = Patient.query.get(patient_id)
    
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    
    prescriptions = patient.prescriptions
    
    return jsonify({
        'prescriptions': [prescription.to_dict() for prescription in prescriptions],
        'total': len(prescriptions)
    }), 200

@bp.route('/<int:patient_id>/bills', methods=['GET'])
@jwt_required()
def get_patient_bills(patient_id):
    """Get all bills for a specific patient."""
    patient = Patient.query.get(patient_id)
    
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    
    bills = patient.bills
    
    return jsonify({
        'bills': [bill.to_dict() for bill in bills],
        'total': len(bills),
        'total_amount': sum(bill.amount for bill in bills),
        'unpaid_amount': sum(bill.due_amount for bill in bills)
    }), 200