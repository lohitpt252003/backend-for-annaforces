from flask import Blueprint, request, jsonify
import sys, os
import json

# Step 1: Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Step 2: Import service
from services.github_services import get_file, add_file, update_file

# Step 3: Blueprint declaration
submissions_bp = Blueprint("submissions", __name__)


