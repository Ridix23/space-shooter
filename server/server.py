from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///space_shooter.db'  # или используйте PostgreSQL на Heroku
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    hashed_password = generate_password_hash(password, method='sha256')
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid email or password'}), 401

    return jsonify({'user_id': user.id, 'message': 'Login successful'}), 200

@app.route('/save_score', methods=['POST'])
def save_score():
    data = request.get_json()
    user_id = data.get('user_id')
    score = data.get('score')
    new_score = Score(user_id=user_id, score=score)
    db.session.add(new_score)
    db.session.commit()
    return jsonify({'message': 'Score saved successfully'}), 201

@app.route('/top_scores', methods=['GET'])
def top_scores():
    scores = Score.query.join(User).add_columns(User.email, Score.score, Score.date).order_by(Score.score.desc()).limit(10).all()
    top_scores = [{'email': email, 'score': score, 'date': date} for email, score, date in scores]
    return jsonify(top_scores), 200

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)