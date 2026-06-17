from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from app.database.db import db
from app.models.user import User

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    
    # Validate input
    required_fields = ['username', 'email', 'password', 'full_name', 'role']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # Create new user
    hashed_password = generate_password_hash(data['password'])
    new_user = User(
        username=data['username'],
        email=data['email'],
        password_hash=hashed_password,
        full_name=data['full_name'],
        role=data['role'],
        department=data.get('department')
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully'}), 201

@bp.route('/login', methods=['POST'])
def login():
    """Login a user and return JWT token."""
    data = request.get_json()
    
    # Validate input
    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400
    
    # Find user
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is disabled'}), 403
    
    # Create access token
    access_token = create_access_token(
        identity={
            'id': user.id,
            'username': user.username,
            'role': user.role
        }
    )
    
    return jsonify({
        'access_token': access_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role,
            'department': user.department
        }
    }), 200

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information."""
    current_user_id = get_jwt_identity()['id']
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200

@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout endpoint (for future token blacklisting)."""
    return jsonify({'message': 'Logged out successfully'}), 200

@bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Forgot password endpoint."""
    data = request.get_json()
    
    if not data.get('email'):
        return jsonify({'error': 'Email required'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user:
        return jsonify({'message': 'Password reset instructions sent if email exists'}), 200
    
    # In a real system, you would send an email with reset instructions
    # This is just a placeholder
    
    return jsonify({'message': 'Password reset instructions sent if email exists'}), 200

@bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password endpoint."""
    data = request.get_json()
    
    # Validate input
    required_fields = ['email', 'new_password', 'reset_token']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # In a real system, you would validate the reset token
    # This is just a placeholder implementation
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user:
        return jsonify({'error': 'Invalid reset token or email'}), 400
    
    # Update password
    user.password_hash = generate_password_hash(data['new_password'])
    db.session.commit()
    
    return jsonify({'message': 'Password reset successfully'}), 200