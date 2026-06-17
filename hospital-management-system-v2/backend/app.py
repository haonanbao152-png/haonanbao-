from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from app.core.config import Config
from app.database.db import db

# Import API routes
from app.api import auth, users, patients, appointments, medications, prescriptions, bills, settings

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)
    JWTManager(app)
    CORS(app, origins=Config.CORS_ORIGINS)
    
    # Register blueprints
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(users.bp, url_prefix='/api/users')
    app.register_blueprint(patients.bp, url_prefix='/api/patients')
    app.register_blueprint(appointments.bp, url_prefix='/api/appointments')
    app.register_blueprint(medications.bp, url_prefix='/api/medications')
    app.register_blueprint(prescriptions.bp, url_prefix='/api/prescriptions')
    app.register_blueprint(bills.bp, url_prefix='/api/bills')
    app.register_blueprint(settings.bp, url_prefix='/api/settings')
    
    @app.route('/')
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'message': 'Hospital Management System API is running',
            'version': '1.0.0'
        })
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)