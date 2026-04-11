from flask import Blueprint, request, jsonify
from backend.decorators import jwt_required, role_required
from backend.auth import log_action
import joblib
import pandas as pd
import os
from backend.models import AuditLog

predict_bp = Blueprint('predict', __name__)

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ml', 'model.joblib')

model_data = None
def load_model():
    global model_data
    if model_data is None:
        if os.path.exists(MODEL_PATH):
            model_data = joblib.load(MODEL_PATH)
            
@predict_bp.route('/evaluate', methods=['POST'])
@jwt_required
def predict_flood(current_user):
    load_model()
    if not model_data:
        return jsonify({'message': 'Model not trained yet.'}), 500
        
    data = request.get_json()
    if not data or 'features' not in data:
        return jsonify({'message': 'No features provided.'}), 400

    features_dict = data['features']
    # Create DataFrame to match model input
    try:
        # Expecting a single row for user prediction
        df = pd.DataFrame([features_dict], columns=model_data['features'])
        # If there are missing columns, fill with 0
        for col in model_data['features']:
            if col not in df.columns:
                df[col] = 0
                
        prediction = model_data['model'].predict(df)[0]
        
        # Determine strict threshold categories
        if prediction < 0.4:
            risk_level = "Low"
        elif prediction <= 0.7:
            risk_level = "Medium"
        else:
            risk_level = "High"

        result = {
            'probability': float(prediction),
            'risk_level': risk_level,
            'feature_importance': model_data['feature_importance']
        }
        
        log_action(current_user.id, 'prediction_results', result)
        
        return jsonify(result), 200
    except Exception as e:
        log_action(current_user.id, 'prediction_error', {'error': str(e)})
        return jsonify({'message': f'Error making prediction: {str(e)}'}), 400

@predict_bp.route('/admin_bulk_evaluate', methods=['POST'])
@jwt_required
@role_required(['Admin', 'Researcher'])
def bulk_predict(current_user):
    return jsonify({'message': 'Bulk evaluation is allowed.'}), 200

@predict_bp.route('/logs', methods=['GET'])
@jwt_required
@role_required(['Admin'])
def get_logs(current_user):
    logs = AuditLog.query.all()
    
    result = []
    for log in logs:
        result.append({
            "user_id": log.user_id,
            "action": log.action,
            "details": log.details,
            "timestamp": str(log.timestamp)
        })
        
    return jsonify(result), 200