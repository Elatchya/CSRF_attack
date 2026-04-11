from flask import Flask
from flask_cors import CORS
from backend.models import db, User
from werkzeug.security import generate_password_hash
import os

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config['SECRET_KEY'] = 'your_super_secret_key_here'#JWT tokens are signed using this
    db_path = os.path.join(os.path.dirname(__file__), 'app.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)#connects database with flask
    
    from backend.auth import auth_bp
    from backend.predict import predict_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(predict_bp, url_prefix='/api/predict')
    
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            hashed_password = generate_password_hash('admin123', method='pbkdf2:sha256')
            admin_user = User(username='admin', password_hash=hashed_password, role='Admin')
            db.session.add(admin_user)
            db.session.commit()
            
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
