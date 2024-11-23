import os
import jwt
import datetime
from flask import Flask, jsonify, request, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from api.models import db, User

api = Blueprint('api', __name__)

SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'your-secret-key')

# Signup endpoint
@api.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"msg": "Email and password are required"}), 400

    user = User.query.filter_by(email=data['email']).first()
    if user:
        return jsonify({"msg": "User already exists"}), 400

    try:
        hashed_password = generate_password_hash(data['password'])
        new_user = User(email=data['email'], password=hashed_password, is_active=True)
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Error creating user: {str(e)}"}), 500

    return jsonify({"msg": "User created successfully"}), 201

# Login endpoint
@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"msg": "Email and password are required"}), 400

    user = User.query.filter_by(email=data['email']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({"msg": "Invalid email or password"}), 401

    try:
        token = jwt.encode({
            "user_id": user.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, SECRET_KEY, algorithm="HS256")
    except Exception as e:
        return jsonify({"msg": f"Token generation failed: {str(e)}"}), 500

    return jsonify({"token": token, "msg": "Login successful"}), 200

# Private route
@api.route('/private', methods=['GET'])
def private():
    token = request.headers.get('Authorization')
    if not token or not token.startswith("Bearer "):
        return jsonify({"msg": "Invalid or missing token"}), 401

    try:
        token = token.split(" ")[1]
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = decoded_token['user_id']
    except jwt.ExpiredSignatureError:
        return jsonify({"msg": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"msg": "Invalid token"}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    return jsonify({"msg": "Access granted", "user": user.serialize()}), 200

