from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
from .. import mongo
from datetime import datetime, timezone

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


@users_blueprint.route("/<user_id>", methods=["GET"])
@jwt_required()
def get_user_by_id(user_id):
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)}, {"deleted": False})
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"]
    }), 200

@users_blueprint.route("/<user_id>", methods=["PUT"])
@jwt_required()
def update_user_by_id(user_id):
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)}, {"deleted": False})
    if not user:
        return jsonify({"error": "User not found"}), 404
    mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": request.json})
    return jsonify({"message": "User updated"}), 200

@users_blueprint.route("/<user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    current_user = get_jwt_identity()
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404
    mongo.db.trash.insert_one({
        "original_user_id": user_id,
        "deleted_at": datetime.now(timezone.utc),
        "deleted_by": current_user,
        "reason": request.json.get("reason", "No reason provided")
    })
    mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"deleted": True}})
    return jsonify({"message": "User soft-deleted"}), 200


@users_blueprint.route("/batch-delete", methods=["POST"])
@jwt_required()
def batch_delete_users():
    data = request.json
    user_ids = data.get("user_ids", [])

    if not user_ids:
        return jsonify({"error": "No user IDs provided"}), 400
    
    current_user = get_jwt_identity()
    users = mongo.db.users.find({"_id": {"$in": [ObjectId(user_id) for user_id in user_ids]}, "deleted":  False})

    for user in users:
        mongo.db.trash.insert_one({
            "original_user_id": user["_id"],
            "deleted_at": datetime.now(timezone.utc),
            "deleted_by": current_user,
            "reason": data.get("reason", "No reason provided")
        })
        mongo.db.users.update_one({"_id": user["_id"]}, {"$set": {"deleted": True}})

    return jsonify({"message": f"soft-deleted {len(user_ids)} users"}), 200


@users_blueprint.route("/trash", methods=["GET"])
@jwt_required()
def view_trash():
    trashed_users = mongo.db.trash.find()
    return jsonify([{
        "id": str(user["original_user_id"]),
        "deleted_at": user["deleted_at"],
        "deleted_by": user["deleted_by"],
        "reason": user["reason"]
    } for user in trashed_users]), 200


@users_blueprint.route("/rest   ore/<user_id>", methods=["POST"])
@jwt_required()
def restore_user(user_id):
    user = mongo.db.trash.find_one({"original_user_id": (user_id)})
    # print(user)
    
    if not user:
        return jsonify({"error":  "User not found"}), 404
    
    mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"deleted": False}})
    mongo.db.trash.delete_one({"original_user_id": (user_id)})
    return jsonify({"message": "User restored"}), 200



@users_blueprint.route("/trash/<user_id>", methods=["DELETE"])
@jwt_required()
def permanent_delete_user(user_id):
    user = mongo.db.trash.find_one({"original_user_id": (user_id)})

    if not user:
        return jsonify({"error":  "User not found"}), 404
    
    mongo.db.trash.delete_one({"original_user_id": (user_id)})
    return jsonify({"message": "User permanently deleted"}), 200