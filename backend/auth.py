from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
import json
from backend.models import db, User, AuditLog
from flask import current_app

auth_bp = Blueprint('auth', __name__)

def log_action(user_id, action, details):
    log = AuditLog(user_id=user_id, action=action, details=json.dumps(details))
    db.session.add(log)
    db.session.commit()

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Missing username or password'}), 400
        
    username = data['username']
    password = data['password']
    role = data.get('role', 'User')

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'User already exists'}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    
    new_user = User(username=username, password_hash=hashed_password, role=role)
    db.session.add(new_user)
    db.session.commit()
    
    log_action(new_user.id, 'register', {'username': username, 'role': role})

    return jsonify({'message': 'User registered successfully!'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Missing credentials'}), 400

    user = User.query.filter_by(username=data['username']).first()

    if not user:
        log_action(None, 'login_failed', {'username': data['username'], 'reason': 'User not found'})
        return jsonify({'message': 'Invalid credentials'}), 401
    
    if user.is_locked:
        log_action(user.id, 'login_failed', {'reason': 'Account locked'})
        return jsonify({'message': 'Account locked due to multiple failed login attempts'}), 403

    if check_password_hash(user.password_hash, data['password']):
        user.failed_login_attempts = 0
        db.session.commit()
        
        # Token expiration set to 1 hour
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }, current_app.config['SECRET_KEY'], algorithm="HS256")
        
        log_action(user.id, 'login_success', {'username': user.username})
        
        return jsonify({
            'token': token,
            'role': user.role,
            'username': user.username
        }), 200
    else:
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= 5:
            user.is_locked = True
        db.session.commit()
        log_action(user.id, 'login_failed', {'reason': 'Incorrect password', 'attempts': user.failed_login_attempts})
        return jsonify({'message': 'Invalid credentials'}), 401
