import logging
from app import mongo


logging.basicConfig(level=logging.INFO)

def test_signup_valid(client, user_data, setup_user_in_db):
    # Call the signup endpoint
    response = client.post("/auth/signup", json=user_data)
    logging.info(f"Response: {response.json}")

    # Validate the response
    assert response.status_code == 201
    assert response.json["message"] == "User registered successfully"

    user = mongo.db.users.find_one({"email": user_data["email"]})
    assert user is not None
    assert user["username"] == user_data["username"]

    mongo.db.users.delete_many({"email": user_data["email"]})


def test_login_valid(client, setup_user_in_db, user_data):
    response = client.post("/auth/login", json={
        "email": user_data["email"], 
        "password": user_data["password"]
        })
    assert response.status_code == 200
    assert "access_token" in response.json


def test_login_invalid_email(client, user_data):
    """
    Test case for login with an invalid email.
    """
    response = client.post("/auth/login", json={
        "email": "invalid@example.com",  # Non-existent email
        "password": user_data["password"]
    })
    
    # Assertions
    assert response.status_code == 401  # Unauthorized
    assert "error" in response.json
    assert response.json["error"] == "Invalid credentials"

def test_login_invalid_password(client, setup_user_in_db, user_data):
    response = client.post("/auth/login", json={"email": user_data["email"], "password": "wrongpassword"})
    assert response.status_code == 401
    assert response.json["error"] == "Invalid credentials"
    
    
def test_login_missing_fields(client):
    response = client.post("/auth/login", json={})
    assert response.status_code == 400
    assert response.json["error"] == "Email and password are required"
    
def test_login_empty_fields(client):
    response = client.post("/auth/login", json={"email": "", "password": ""})
    assert response.status_code == 400
    assert response.json["error"] == "Email and password are required"
    
def test_login_invalid_credentials(client, user_data):
    response = client.post("/auth/login", json={
        "email": user_data["email"],
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert response.json["error"] == "Invalid credentials"