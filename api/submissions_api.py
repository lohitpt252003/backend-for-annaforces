from flask import Blueprint, jsonify
from services.github_services import get_folder_contents
import json

submissions_bp = Blueprint('submissions_bp', __name__)

