from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
from .. import mongo
from datetime import datetime

users_blueprint = Blueprint("users", __name__, url_prefix="/users")

@users_blueprint.route("/", methods=["GET"])
@jwt_required()
def get_users():
    users = mongo.db.users.find({"deleted": False})
    return jsonify([{
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"]
    } for user in users]), 200


@users_blueprint.route("/<user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    current_user = get_jwt_identity()
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404
    mongo.db.trash.insert_one({
        "original_user_id": user_id,
        "deleted_at": datetime.utcnow(),
        "deleted_by": current_user,
        "reason": request.json.get("reason", "No reason provided")
    })
    mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"deleted": True}})
    return jsonify({"message": "User soft-deleted"}), 200
