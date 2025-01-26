from datetime import datetime

def get_user_model():
    return {
        "username": None,
        "email": None,
        "password": None,  # Hashed password
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "deleted": False
    }

def get_trash_model():
    return {
        "original_user_id": None,
        "deleted_at": datetime.utcnow(),
        "deleted_by": None,
        "reason": None
    }