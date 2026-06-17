from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import date, datetime
from app.database.db import db
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.models.user import User

bp = Blueprint('appointments', __name__)

@bp.route('/', methods=['GET'])
@jwt_required()
def get_appointments():
    """Get all appointments with filtering and pagination."""
    current_user = get_jwt_identity()
    
    # Query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')
    date_filter = request.args.get('date')
    doctor_id = request.args.get('doctor_id', type=int)
    patient_id = request.args.get('patient_id', type=int)
    
    # Base query
    query = Appointment.query
    
    # Apply filters
    if status:
        query = query.filter_by(status=status)
    
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter_by(date=filter_date)
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    if doctor_id:
        query = query.filter_by(doctor_id=doctor_id)
    
    if patient_id:
        query = query.filter_by(patient_id=patient_id)
    
    # For non-admin users, only show their own appointments
    if current_user['role'] != 'admin' and current_user['role'] != 'receptionist':
        query = query.filter_by(doctor_id=current_user['id'])
    
    # Pagination
    pagination = query.order_by(Appointment.date.desc(), Appointment.start_time).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    appointments = pagination.items
    total = pagination.total
    
    return jsonify({
        'appointments': [appointment.to_dict() for appointment in appointments],
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': pagination.pages
    }), 200

@bp.route('/<int:appointment_id>', methods=['GET'])
@jwt_required()
def get_appointment(appointment_id):
    """Get a specific appointment by ID."""
    appointment = Appointment.query.get(appointment_id)
    
    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404
    
    # Check permissions
    current_user = get_jwt_identity()
    if (current_user['role'] != 'admin' and 
        current_user['role'] != 'receptionist' and 
        appointment.doctor_id != current_user['id']):
        return jsonify({'error': 'Permission denied'}), 403
    
    return jsonify(appointment.to_dict()), 200

@bp.route('/', methods=['POST'])
@jwt_required()
def create_appointment():
    """Create a new appointment."""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['patient_id', 'doctor_id', 'appointment_type', 'date', 'start_time', 'end_time']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Validate patient exists
    patient = Patient.query.get(data['patient_id'])
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    
    # Validate doctor exists
    doctor = User.query.get(data['doctor_id'])
    if not doctor or doctor.role != 'doctor':
        return jsonify({'error': 'Doctor not found'}), 404
    
    # Check for time conflicts
    conflicts = Appointment.query.filter(
        Appointment.doctor_id == data['doctor_id'],
        Appointment.date == data['date'],
        Appointment.status == 'scheduled',
        ((Appointment.start_time <= data['start_time'] & Appointment.end_time > data['start_time']) |
         (Appointment.start_time < data['end_time'] & Appointment.end_time >= data['end_time']) |
         (Appointment.start_time >= data['start_time'] & Appointment.end_time <= data['end_time']))
    ).first()
    
    if conflicts:
        return jsonify({'error': 'Time slot already booked for this doctor'}), 409
    
    # Create new appointment
    new_appointment = Appointment(**data)
    
    try:
        db.session.add(new_appointment)
        db.session.commit()
        return jsonify(new_appointment.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/<int:appointment_id>', methods=['PUT'])
@jwt_required()
def update_appointment(appointment_id):
    """Update an existing appointment."""
    appointment = Appointment.query.get(appointment_id)
    
    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404
    
    # Check permissions
    current_user = get_jwt_identity()
    if (current_user['role'] != 'admin' and 
        current_user['role'] != 'receptionist' and 
        appointment.doctor_id != current_user['id']):
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    
    # Update appointment fields
    for key, value in data.items():
        if hasattr(appointment, key):
            setattr(appointment, key, value)
    
    try:
        db.session.commit()
        return jsonify(appointment.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/<int:appointment_id>', methods=['DELETE'])
@jwt_required()
def delete_appointment(appointment_id):
    """Delete an appointment."""
    appointment = Appointment.query.get(appointment_id)
    
    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404
    
    # Check permissions
    current_user = get_jwt_identity()
    if (current_user['role'] != 'admin' and 
        current_user['role'] != 'receptionist'):
        return jsonify({'error': 'Permission denied'}), 403
    
    try:
        db.session.delete(appointment)
        db.session.commit()
        return jsonify({'message': 'Appointment deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/today', methods=['GET'])
@jwt_required()
def get_today_appointments():
    """Get all appointments for today."""
    current_user = get_jwt_identity()
    
    # Base query for today's appointments
    query = Appointment.query.filter_by(date=date.today())
    
    # For non-admin users, only show their own appointments
    if current_user['role'] != 'admin' and current_user['role'] != 'receptionist':
        query = query.filter_by(doctor_id=current_user['id'])
    
    appointments = query.order_by(Appointment.start_time).all()
    
    return jsonify({
        'appointments': [appointment.to_dict() for appointment in appointments],
        'total': len(appointments)
    }), 200

@bp.route('/<int:appointment_id>/status', methods=['PATCH'])
@jwt_required()
def update_appointment_status(appointment_id):
    """Update appointment status."""
    appointment = Appointment.query.get(appointment_id)
    
    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404
    
    data = request.get_json()
    new_status = data.get('status')
    
    if not new_status:
        return jsonify({'error': 'Status is required'}), 400
    
    # Validate status
    valid_statuses = ['scheduled', 'completed', 'cancelled', 'no_show']
    if new_status not in valid_statuses:
        return jsonify({'error': f'Invalid status. Use one of: {valid_statuses}'}), 400
    
    appointment.status = new_status
    
    try:
        db.session.commit()
        return jsonify(appointment.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400