from flask import Blueprint, request, jsonify
import sys, os
import json
from functools import wraps
from utils.jwt_token import validate_token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = validate_token(token)
            if not data['valid']:
                return jsonify({'message': data['error']}), 401
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(*args, **kwargs)
    return decorated

# Step 1: Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Step 2: Import service
from services.github_services import get_file, add_file, update_file

# Step 3: Blueprint declaration
admin_bp = Blueprint("admin", __name__)