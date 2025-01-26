from flask_jwt_extended import create_access_token
from app import mongo
from bson import ObjectId
from datetime import timezone, datetime

# Test for GET /users (list users)
def test_get_users(client, setup_user_in_db, app):
    with app.app_context():
        # Generate access token
        access_token = create_access_token(identity="user_id")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/users/", headers=headers)
    
    assert response.status_code == 200
    assert isinstance(response.json, list)
    


def test_get_user_by_id(client, setup_user_in_db, app):
    with app.app_context():
        access_token = create_access_token(identity="user_id")
    
    user_data = setup_user_in_db
    user_id = str(mongo.db.users.find_one({"email": user_data["email"]})["_id"])
    
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get(f"/users/{user_id}", headers=headers)
    
    assert response.status_code == 200
    assert response.json["email"] == user_data["email"]
    
    
def test_update_user_by_id(client, setup_user_in_db, app):
    with app.app_context():
        access_token = create_access_token(identity="user_id")
    
    user_data = setup_user_in_db
    user_id = str(mongo.db.users.find_one({"email": user_data["email"]})["_id"])
    
    headers = {"Authorization": f"Bearer {access_token}"}
    update_data = {"username": "updated_username"}
    response = client.put(f"/users/{user_id}", json=update_data, headers=headers)
    
    assert response.status_code == 200
    assert response.json["message"] == "User updated"
    
    
def test_delete_user(client, setup_user_in_db, app):
    with app.app_context():
        access_token = create_access_token(identity="user_id")
    
    user_data = setup_user_in_db
    user_id = str(mongo.db.users.find_one({"email": user_data["email"]})["_id"])
    
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.delete(f"/users/{user_id}", json={"reason": "Test delete"}, headers=headers)
    
    assert response.status_code == 200
    assert response.json["message"] == "User soft-deleted"
    
    
def test_batch_delete_users(client, setup_user_in_db, app):
    with app.app_context():
        access_token = create_access_token(identity="user_id")
    
    user_data = setup_user_in_db
    user_id = str(mongo.db.users.find_one({"email": user_data["email"]})["_id"])
    
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post("/users/batch-delete", json={"user_ids": [user_id]}, headers=headers)
    
    assert response.status_code == 200
    assert response.json["message"] == "soft-deleted 1 users"
    


def test_view_trash(client, setup_user_in_db, app):
    with app.app_context():
        access_token = create_access_token(identity="user_id")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/users/trash", headers=headers)
    
    assert response.status_code == 200
    assert isinstance(response.json, list)
    

def test_restore_user(client, setup_user_in_db, app):
    with app.app_context():
        access_token = create_access_token(identity="user_id")

    user_data = setup_user_in_db
    user_id = str(mongo.db.users.find_one({"email": user_data["email"]})["_id"])

    # Soft delete user before restoring
    mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"deleted": True}})
    
    # Add the user to trash for restoration
    mongo.db.trash.insert_one({
        "original_user_id": ObjectId(user_id),
        "deleted_at": datetime.now(timezone.utc),
        "deleted_by": "user_id",
        "reason": "Test"
    })

    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post(f"/users/restore/{user_id}", headers=headers)

    assert response.status_code ==200
    assert response.json["message"] == "User restored"    
    


def test_permanent_delete_user(client, setup_user_in_db, app):
    with app.app_context():
        access_token = create_access_token(identity="user_id")

    user_data = setup_user_in_db
    user_id = str(mongo.db.users.find_one({"email": user_data["email"]})["_id"])

    # Soft delete user before permanent deletion
    mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"deleted": True}})

    # Add the user to the trash collection
    mongo.db.trash.insert_one({
        "original_user_id": ObjectId(user_id),
        "deleted_at": datetime.now(timezone.utc),
        "deleted_by": "user_id",
        "reason": "Test"
    })

    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.delete(f"/users/trash/{user_id}", headers=headers)

    assert response.status_code == 200
    assert response.json["message"] == "User permanently deleted"