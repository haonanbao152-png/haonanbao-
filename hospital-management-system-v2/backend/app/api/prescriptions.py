from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database.db import db
from app.models.prescription import Prescription, PrescriptionItem
from app.models.patient import Patient
from app.models.medication import Medication

bp = Blueprint('prescriptions', __name__)

@bp.route('/', methods=['GET'])
@jwt_required()
def get_prescriptions():
    """Get all prescriptions with filtering and pagination."""
    current_user = get_jwt_identity()
    
    # Query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')
    patient_id = request.args.get('patient_id', type=int)
    doctor_id = request.args.get('doctor_id', type=int)
    
    # Base query
    query = Prescription.query
    
    # Apply filters
    if status:
        query = query.filter_by(status=status)
    
    if patient_id:
        query = query.filter_by(patient_id=patient_id)
    
    if doctor_id:
        query = query.filter_by(doctor_id=doctor_id)
    
    # For non-admin users, only show their own prescriptions
    if current_user['role'] == 'doctor':
        query = query.filter_by(doctor_id=current_user['id'])
    
    # Pagination
    pagination = query.order_by(Prescription.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    prescriptions = pagination.items
    total = pagination.total
    
    return jsonify({
        'prescriptions': [prescription.to_dict() for prescription in prescriptions],
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': pagination.pages
    }), 200

@bp.route('/<int:prescription_id>', methods=['GET'])
@jwt_required()
def get_prescription(prescription_id):
    """Get a specific prescription by ID."""
    prescription = Prescription.query.get(prescription_id)
    
    if not prescription:
        return jsonify({'error': 'Prescription not found'}), 404
    
    # Check permissions
    current_user = get_jwt_identity()
    if (current_user['role'] != 'admin' and 
        current_user['role'] != 'pharmacist' and 
        prescription.doctor_id != current_user['id']):
        return jsonify({'error': 'Permission denied'}), 403
    
    return jsonify(prescription.to_dict()), 200

@bp.route('/', methods=['POST'])
@jwt_required()
def create_prescription():
    """Create a new prescription."""
    current_user = get_jwt_identity()
    
    # Check if user is a doctor
    if current_user['role'] != 'doctor' and current_user['role'] != 'admin':
        return jsonify({'error': 'Only doctors can create prescriptions'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['patient_id', 'diagnosis', 'items']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if not data['items'] or not isinstance(data['items'], list):
        return jsonify({'error': 'Prescription must have at least one medication item'}), 400
    
    # Validate patient exists
    patient = Patient.query.get(data['patient_id'])
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    
    # Create prescription
    prescription_data = {
        'patient_id': data['patient_id'],
        'doctor_id': current_user['id'],
        'appointment_id': data.get('appointment_id'),
        'diagnosis': data['diagnosis'],
        'notes': data.get('notes', '')
    }
    
    new_prescription = Prescription(**prescription_data)
    
    try:
        db.session.add(new_prescription)
        db.session.flush()  # Get the prescription ID
        
        # Create prescription items
        for item_data in data['items']:
            # Validate medication exists
            medication = Medication.query.get(item_data['medication_id'])
            if not medication:
                raise ValueError(f'Medication with ID {item_data["medication_id"]} not found')
            
            # Validate item required fields
            item_required_fields = ['medication_id', 'dosage', 'frequency', 'duration']
            if not all(field in item_data for field in item_required_fields):
                raise ValueError('Missing required fields in prescription item')
            
            # Create prescription item
            prescription_item = PrescriptionItem(
                prescription_id=new_prescription.id,
                **item_data
            )
            db.session.add(prescription_item)
        
        db.session.commit()
        
        # Refresh to load relationships
        db.session.refresh(new_prescription)
        
        return jsonify(new_prescription.to_dict()), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/<int:prescription_id>', methods=['PUT'])
@jwt_required()
def update_prescription(prescription_id):
    """Update an existing prescription."""
    prescription = Prescription.query.get(prescription_id)
    
    if not prescription:
        return jsonify({'error': 'Prescription not found'}), 404
    
    current_user = get_jwt_identity()
    
    # Check permissions
    if (current_user['role'] != 'admin' and 
        prescription.doctor_id != current_user['id']):
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    
    # Update basic prescription fields
    updatable_fields = ['diagnosis', 'notes', 'status']
    for field in updatable_fields:
        if field in data:
            setattr(prescription, field, data[field])
    
    try:
        db.session.commit()
        return jsonify(prescription.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/<int:prescription_id>', methods=['DELETE'])
@jwt_required()
def delete_prescription(prescription_id):
    """Delete a prescription."""
    prescription = Prescription.query.get(prescription_id)
    
    if not prescription:
        return jsonify({'error': 'Prescription not found'}), 404
    
    current_user = get_jwt_identity()
    
    # Check permissions
    if (current_user['role'] != 'admin' and 
        prescription.doctor_id != current_user['id']):
        return jsonify({'error': 'Permission denied'}), 403
    
    try:
        db.session.delete(prescription)
        db.session.commit()
        return jsonify({'message': 'Prescription deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/<int:prescription_id>/status', methods=['PATCH'])
@jwt_required()
def update_prescription_status(prescription_id):
    """Update prescription status."""
    prescription = Prescription.query.get(prescription_id)
    
    if not prescription:
        return jsonify({'error': 'Prescription not found'}), 404
    
    current_user = get_jwt_identity()
    
    # Check permissions
    if (current_user['role'] != 'admin' and 
        current_user['role'] != 'pharmacist' and 
        prescription.doctor_id != current_user['id']):
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    new_status = data.get('status')
    
    if not new_status:
        return jsonify({'error': 'Status is required'}), 400
    
    # Validate status
    valid_statuses = ['active', 'filled', 'cancelled']
    if new_status not in valid_statuses:
        return jsonify({'error': f'Invalid status. Use one of: {valid_statuses}'}), 400
    
    prescription.status = new_status
    
    try:
        db.session.commit()
        return jsonify(prescription.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/patient/<int:patient_id>', methods=['GET'])
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

@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_prescription_stats():
    """Get prescription statistics."""
    from sqlalchemy import func
    
    current_user = get_jwt_identity()
    
    # Base query
    query = Prescription.query
    
    # For doctors, only show their own statistics
    if current_user['role'] == 'doctor':
        query = query.filter_by(doctor_id=current_user['id'])
    
    # Total prescriptions
    total = query.count()
    
    # Prescriptions by status
    status_counts = db.session.query(
        Prescription.status,
        func.count(Prescription.id)
    ).group_by(Prescription.status).all()
    
    # Total medication items prescribed
    total_items = db.session.query(func.count(PrescriptionItem.id)).scalar() or 0
    
    return jsonify({
        'total_prescriptions': total,
        'prescriptions_by_status': [
            {'status': status, 'count': count} for status, count in status_counts
        ],
        'total_medication_items': total_items
    }), 200