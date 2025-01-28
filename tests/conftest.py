import pytest
from app import create_app, mongo
from werkzeug.security import generate_password_hash
import logging
from datetime import datetime, timezone
from app.models import db_models


logging.basicConfig(level=logging.INFO)

@pytest.fixture
def app():
    app = create_app()
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def user_data():
    return {
        "username": "user",
        "email": "user@example.com",
        "password": "userpassword"
    }

@pytest.fixture
def login_data():
    return {
        "email": "user@example.com",
        "password": "userpassword"
    }
    

@pytest.fixture
def setup_user_in_db(user_data):
    
    hashed_password = generate_password_hash(user_data["password"])
    
    existing_user = mongo.db.users.find_one({"email": user_data["email"]})
    
    if not existing_user:
        user_model = db_models.get_user_model()
        
        user_model["username"] = user_data["username"]
        user_model["email"] = user_data["email"]
        user_model["password"] = hashed_password
        user_model["deleted"] = False
        user_model["created_at"] = user_model["updated_at"] = datetime.now(timezone.utc)
        
        mongo.db.users.insert_one(user_model)
        
        logging.info(f"Inserted user: {user_data['email']}")
    else:
        logging.info(f"User {user_data['email']} already exists.")

    inserted_user = mongo.db.users.find_one({"email": user_data["email"]})
    assert inserted_user is not None
    
    yield user_data
    
    # Teardown - delete all users with the same email
    result = mongo.db.users.delete_many({"email": user_data["email"]})
    if result.deleted_count > 0:
        logging.info(f"Deleted {result.deleted_count} user(s) with email: {user_data['email']}")
    else:
        logging.warning(f"No users found for deletion with email: {user_data['email']}")