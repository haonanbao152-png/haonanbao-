from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database.db import db
from app.models.medication import Medication

bp = Blueprint('medications', __name__)

@bp.route('/', methods=['GET'])
@jwt_required()
def get_medications():
    """Get all medications with pagination and search."""
    # Query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    low_stock = request.args.get('low_stock', type=bool, default=False)
    
    # Base query
    query = Medication.query
    
    # Search functionality
    if search:
        search_term = f'%{search}%'
        query = query.filter(
            (Medication.name.ilike(search_term)) |
            (Medication.description.ilike(search_term)) |
            (Medication.manufacturer.ilike(search_term))
        )
    
    # Low stock filter
    if low_stock:
        query = query.filter(Medication.stock_quantity < 50)  # Consider items with less than 50 units as low stock
    
    # Pagination
    pagination = query.order_by(Medication.name).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    medications = pagination.items
    total = pagination.total
    
    return jsonify({
        'medications': [medication.to_dict() for medication in medications],
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': pagination.pages
    }), 200

@bp.route('/<int:medication_id>', methods=['GET'])
@jwt_required()
def get_medication(medication_id):
    """Get a specific medication by ID."""
    medication = Medication.query.get(medication_id)
    
    if not medication:
        return jsonify({'error': 'Medication not found'}), 404
    
    return jsonify(medication.to_dict()), 200

@bp.route('/', methods=['POST'])
@jwt_required()
def create_medication():
    """Create a new medication."""
    current_user = get_jwt_identity()
    
    # Check permissions
    if current_user['role'] not in ['admin', 'pharmacist']:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'dosage_form', 'strength', 'unit_price']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if medication already exists
    existing = Medication.query.filter_by(
        name=data['name'],
        strength=data['strength'],
        dosage_form=data['dosage_form']
    ).first()
    
    if existing:
        return jsonify({'error': 'Medication with this name, strength and form already exists'}), 400
    
    # Create new medication
    new_medication = Medication(**data)
    
    try:
        db.session.add(new_medication)
        db.session.commit()
        return jsonify(new_medication.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/<int:medication_id>', methods=['PUT'])
@jwt_required()
def update_medication(medication_id):
    """Update an existing medication."""
    current_user = get_jwt_identity()
    
    # Check permissions
    if current_user['role'] not in ['admin', 'pharmacist']:
        return jsonify({'error': 'Permission denied'}), 403
    
    medication = Medication.query.get(medication_id)
    
    if not medication:
        return jsonify({'error': 'Medication not found'}), 404
    
    data = request.get_json()
    
    # Update medication fields
    for key, value in data.items():
        if hasattr(medication, key):
            setattr(medication, key, value)
    
    try:
        db.session.commit()
        return jsonify(medication.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/<int:medication_id>', methods=['DELETE'])
@jwt_required()
def delete_medication(medication_id):
    """Delete a medication."""
    current_user = get_jwt_identity()
    
    # Check permissions
    if current_user['role'] != 'admin':
        return jsonify({'error': 'Permission denied'}), 403
    
    medication = Medication.query.get(medication_id)
    
    if not medication:
        return jsonify({'error': 'Medication not found'}), 404
    
    try:
        db.session.delete(medication)
        db.session.commit()
        return jsonify({'message': 'Medication deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/<int:medication_id>/stock', methods=['PATCH'])
@jwt_required()
def update_stock(medication_id):
    """Update medication stock quantity."""
    current_user = get_jwt_identity()
    
    # Check permissions
    if current_user['role'] not in ['admin', 'pharmacist']:
        return jsonify({'error': 'Permission denied'}), 403
    
    medication = Medication.query.get(medication_id)
    
    if not medication:
        return jsonify({'error': 'Medication not found'}), 404
    
    data = request.get_json()
    quantity_change = data.get('quantity_change', 0)
    
    if not isinstance(quantity_change, int):
        return jsonify({'error': 'Quantity change must be an integer'}), 400
    
    # Update stock
    new_quantity = medication.stock_quantity + quantity_change
    
    if new_quantity < 0:
        return jsonify({'error': 'Insufficient stock. Cannot reduce below zero'}), 400
    
    medication.stock_quantity = new_quantity
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Stock updated successfully',
            'medication': medication.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/low-stock', methods=['GET'])
@jwt_required()
def get_low_stock_medications():
    """Get all medications with low stock levels."""
    # Define low stock threshold
    threshold = request.args.get('threshold', 50, type=int)
    
    medications = Medication.query.filter(Medication.stock_quantity < threshold).all()
    
    return jsonify({
        'medications': [medication.to_dict() for medication in medications],
        'total': len(medications),
        'threshold': threshold
    }), 200

@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_medication_stats():
    """Get medication statistics."""
    from sqlalchemy import func
    
    # Total medications
    total = Medication.query.count()
    
    # Low stock count
    low_stock_count = Medication.query.filter(Medication.stock_quantity < 50).count()
    
    # Total stock value
    total_value = db.session.query(func.sum(Medication.stock_quantity * Medication.unit_price)).scalar() or 0
    
    # Medications by form
    form_counts = db.session.query(
        Medication.dosage_form,
        func.count(Medication.id)
    ).group_by(Medication.dosage_form).all()
    
    return jsonify({
        'total_medications': total,
        'low_stock_count': low_stock_count,
        'total_stock_value': float(total_value),
        'medications_by_form': [
            {'form': form, 'count': count} for form, count in form_counts
        ]
    }), 200