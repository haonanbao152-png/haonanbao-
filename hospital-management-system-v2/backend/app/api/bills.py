from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app.database.db import db
from app.models.bill import Bill
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.prescription import Prescription

bp = Blueprint('bills', __name__)

@bp.route('/', methods=['GET'])
@jwt_required()
def get_bills():
    """Get all bills with filtering and pagination."""
    current_user = get_jwt_identity()
    
    # Query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')
    patient_id = request.args.get('patient_id', type=int)
    
    # Base query
    query = Bill.query
    
    # Apply filters
    if status:
        query = query.filter_by(status=status)
    
    if patient_id:
        query = query.filter_by(patient_id=patient_id)
    
    # Pagination
    pagination = query.order_by(Bill.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    bills = pagination.items
    total = pagination.total
    
    return jsonify({
        'bills': [bill.to_dict() for bill in bills],
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': pagination.pages
    }), 200

@bp.route('/<int:bill_id>', methods=['GET'])
@jwt_required()
def get_bill(bill_id):
    """Get a specific bill by ID."""
    bill = Bill.query.get(bill_id)
    
    if not bill:
        return jsonify({'error': 'Bill not found'}), 404
    
    return jsonify(bill.to_dict()), 200

@bp.route('/', methods=['POST'])
@jwt_required()
def create_bill():
    """Create a new bill."""
    current_user = get_jwt_identity()
    
    # Check permissions
    if current_user['role'] not in ['admin', 'receptionist', 'billing']:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['patient_id', 'amount']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Validate patient exists
    patient = Patient.query.get(data['patient_id'])
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    
    # Validate appointment if provided
    if data.get('appointment_id'):
        appointment = Appointment.query.get(data['appointment_id'])
        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404
    
    # Validate prescription if provided
    if data.get('prescription_id'):
        prescription = Prescription.query.get(data['prescription_id'])
        if not prescription:
            return jsonify({'error': 'Prescription not found'}), 404
    
    # Create new bill
    new_bill = Bill(**data)
    
    try:
        db.session.add(new_bill)
        db.session.commit()
        return jsonify(new_bill.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/<int:bill_id>', methods=['PUT'])
@jwt_required()
def update_bill(bill_id):
    """Update an existing bill."""
    current_user = get_jwt_identity()
    
    # Check permissions
    if current_user['role'] not in ['admin', 'receptionist', 'billing']:
        return jsonify({'error': 'Permission denied'}), 403
    
    bill = Bill.query.get(bill_id)
    
    if not bill:
        return jsonify({'error': 'Bill not found'}), 404
    
    data = request.get_json()
    
    # Update bill fields (excluding payment fields)
    updatable_fields = ['amount', 'notes']
    for field in updatable_fields:
        if field in data:
            setattr(bill, field, data[field])
    
    try:
        db.session.commit()
        return jsonify(bill.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/<int:bill_id>/pay', methods=['POST'])
@jwt_required()
def pay_bill(bill_id):
    """Process payment for a bill."""
    current_user = get_jwt_identity()
    
    # Check permissions
    if current_user['role'] not in ['admin', 'receptionist', 'billing']:
        return jsonify({'error': 'Permission denied'}), 403
    
    bill = Bill.query.get(bill_id)
    
    if not bill:
        return jsonify({'error': 'Bill not found'}), 404
    
    if bill.status == 'paid':
        return jsonify({'error': 'Bill is already paid'}), 400
    
    data = request.get_json()
    
    # Validate payment data
    if not data.get('payment_method'):
        return jsonify({'error': 'Payment method is required'}), 400
    
    # Update bill with payment information
    bill.status = 'paid'
    bill.payment_method = data['payment_method']
    bill.payment_date = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Payment processed successfully',
            'bill': bill.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/<int:bill_id>/partial-payment', methods=['POST'])
@jwt_required()
def partial_payment(bill_id):
    """Process partial payment for a bill."""
    current_user = get_jwt_identity()
    
    # Check permissions
    if current_user['role'] not in ['admin', 'receptionist', 'billing']:
        return jsonify({'error': 'Permission denied'}), 403
    
    bill = Bill.query.get(bill_id)
    
    if not bill:
        return jsonify({'error': 'Bill not found'}), 404
    
    if bill.status == 'paid':
        return jsonify({'error': 'Bill is already fully paid'}), 400
    
    data = request.get_json()
    
    # Validate payment data
    if not data.get('payment_amount') or not data.get('payment_method'):
        return jsonify({'error': 'Payment amount and method are required'}), 400
    
    payment_amount = float(data['payment_amount'])
    
    if payment_amount <= 0:
        return jsonify({'error': 'Payment amount must be greater than zero'}), 400
    
    if payment_amount > bill.amount:
        return jsonify({'error': 'Payment amount cannot exceed bill amount'}), 400
    
    # In a real system, you would track partial payments
    # This is a simplified implementation
    
    # Update bill status
    if payment_amount == bill.amount:
        bill.status = 'paid'
        bill.payment_method = data['payment_method']
        bill.payment_date = datetime.utcnow()
    else:
        bill.status = 'partially_paid'
        # Track partial payment (in a real system, you would have a separate table)
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Partial payment processed successfully',
            'bill': bill.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/patient/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_patient_bills(patient_id):
    """Get all bills for a specific patient."""
    patient = Patient.query.get(patient_id)
    
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    
    bills = patient.bills
    
    # Calculate financial summary
    total_amount = sum(bill.amount for bill in bills)
    paid_amount = sum(bill.amount for bill in bills if bill.status == 'paid')
    partially_paid_amount = sum(bill.amount * 0.5 for bill in bills if bill.status == 'partially_paid')  # Example
    unpaid_amount = total_amount - paid_amount - partially_paid_amount
    
    return jsonify({
        'bills': [bill.to_dict() for bill in bills],
        'total': len(bills),
        'financial_summary': {
            'total_amount': float(total_amount),
            'paid_amount': float(paid_amount),
            'partially_paid_amount': float(partially_paid_amount),
            'unpaid_amount': float(unpaid_amount)
        }
    }), 200

@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_billing_stats():
    """Get billing statistics."""
    from sqlalchemy import func
    
    # Total bills
    total = Bill.query.count()
    
    # Bills by status
    status_counts = db.session.query(
        Bill.status,
        func.count(Bill.id)
    ).group_by(Bill.status).all()
    
    # Total revenue
    total_revenue = db.session.query(func.sum(Bill.amount)).filter(
        Bill.status.in_(['paid', 'partially_paid'])
    ).scalar() or 0
    
    # Unpaid revenue
    unpaid_revenue = db.session.query(func.sum(Bill.amount)).filter_by(
        status='unpaid'
    ).scalar() or 0
    
    # Monthly revenue (last 6 months)
    from datetime import datetime, timedelta
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    
    monthly_revenue = db.session.query(
        func.date_trunc('month', Bill.created_at).label('month'),
        func.sum(Bill.amount).label('revenue')
    ).filter(
        Bill.created_at >= six_months_ago,
        Bill.status.in_(['paid', 'partially_paid'])
    ).group_by('month').order_by('month').all()
    
    return jsonify({
        'total_bills': total,
        'bills_by_status': [
            {'status': status, 'count': count} for status, count in status_counts
        ],
        'total_revenue': float(total_revenue),
        'unpaid_revenue': float(unpaid_revenue),
        'monthly_revenue': [
            {
                'month': month.strftime('%Y-%m') if month else None,
                'revenue': float(revenue) if revenue else 0.0
            }
            for month, revenue in monthly_revenue
        ]
    }), 200