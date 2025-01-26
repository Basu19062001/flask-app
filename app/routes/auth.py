from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import check_password_hash, generate_password_hash
from .. import mongo


auth_blueprint = Blueprint("auth", __name__, url_prefix="/auth")

@auth_blueprint.route("/signup", methods=["POST"])
def signup():
    data = request.json
    if not data or not all(k in data for k in ("username", "email", "password")):
        return jsonify({"error": "Invalid input"}), 400
    hashed_password = generate_password_hash(data["password"])
    data["password"] = hashed_password
    data["deleted"] = False
    mongo.db.users.insert_one(data)
    return jsonify({"message": "User registered successfully"}), 201

@auth_blueprint.route("/login", methods=["POST"] )
def login():
    data = request.json
    if not data or not all(k in data for k in ("email", "password")) or not data["email"].strip() or not data["password"].strip():
        return jsonify({"error": "Email and password are required"}), 400
    
    user = mongo.db.users.find_one({"email": data["email"]})
    
    if user and check_password_hash(user["password"], data["password"]):
        access_token = create_access_token(identity=str(user["_id"]))
        # refresh_token = create_refresh_token(identity=str(user["_id"]))
        return jsonify({"access_token": access_token}), 200
    
    return jsonify({"error": "Invalid credentials"}), 401