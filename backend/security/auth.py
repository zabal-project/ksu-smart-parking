from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token

def hash_password(password):
    return generate_password_hash(password)

def verify_password(password_hash, password):
    return check_password_hash(password_hash, password)

def generate_token(user_id, role):
    additional_claims = {"role": role}
    return create_access_token(identity=str(user_id), additional_claims=additional_claims)
