from flask_jwt_extended import decode_token

def decode_jwt(token):
    return decode_token(token)