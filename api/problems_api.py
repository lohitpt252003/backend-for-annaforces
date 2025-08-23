from flask import Blueprint, jsonify, request
import sys
import os
import json
import time


from services.github_services import get_file, get_folder_contents, add_file
from config.github_config import GITHUB_PROBLEMS_BASE_PATH

# Blueprint declaration
problems_bp = Blueprint("problems", __name__)

@problems_bp.route('/', methods=['GET'])
def get_problems():
    pass

@problems_bp.route('/<problem_id>', methods=['GET'])
def get_problem_by_id(problem_id):
    pass

@problems_bp.route('/<problem_id>/submit', methods=['POST'])
def submit_problem(problem_id):
    pass

@problems_bp.route('/<problem_id>/submissions', methods=['GET'])
def get_problem_submissions(problem_id):
    pass

@problems_bp.route('/add', methods=['POST'])
def add_problem():
    pass