# import logging
# import pytest
# from flask_jwt_extended import create_access_token

# logging.basicConfig(level=logging.DEBUG)

# @pytest.fixture
# def token(client, setup_user_in_db, app):
#     user_data = setup_user_in_db
#     with app.app_context():  # Ensure app context is available
#         access_token = create_access_token(identity=user_data["email"])
#     return access_token

# def test_get_users(client, token, setup_user_in_db):
#     response = client.get("/users/", headers={"Authorization": f"Bearer {token}"})
#     logging.debug("Response: %s", response.json)
#     assert response.status_code == 200
#     assert len(response.json) > 0
#     assert response.json[0]["email"] == setup_user_in_db["email"]