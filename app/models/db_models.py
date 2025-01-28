from datetime import datetime, timezone

def get_user_model():
    return {
        "username": None,
        "email": None,
        "password": None,  # Hashed password
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "deleted": False
    }

def get_trash_model():
    return {
        "original_user_id": None,
        "deleted_at": datetime.now(timezone.utc),
        "deleted_by": None,
        "reason": None
    }