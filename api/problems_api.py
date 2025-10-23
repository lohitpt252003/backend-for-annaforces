from flask import Blueprint, jsonify, request
from services import problem_service, submission_service, judge_service
from utils.jwt_token import validate_token
from functools import wraps

problems_bp = Blueprint("problems", __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        result = validate_token(token)
        if not result['valid']:
            return jsonify({'message': result['error']}), 401

        current_user = result['data']
        return f(current_user, *args, **kwargs)
    return decorated

@problems_bp.route('/', methods=['GET'])
@token_required
def get_problems(current_user):
    search_term = request.args.get('search', '').lower()
    filter_difficulty = request.args.get('difficulty', '').lower()
    filter_tag = request.args.get('tag', '').lower()

    problems, error = problem_service.get_all_problems_metadata()

    if error:
        return jsonify({"error": error["message"]}), 500

    # Apply filters
    filtered_problems = []
    for problem in problems:
        # Search filter
        if search_term and not (
            search_term in problem.get('title', '').lower() or
            search_term in problem.get('id', '').lower()
        ):
            continue

        # Difficulty filter
        if filter_difficulty and problem.get('difficulty', '').lower() != filter_difficulty:
            continue

        # Tag filter
        if filter_tag and not any(tag.lower() == filter_tag for tag in problem.get('tags', [])):
            continue

        filtered_problems.append(problem)

    total_problems = len(filtered_problems)
    
    problems_dict = {problem['id']: problem for problem in filtered_problems}

    return jsonify({
        'problems': problems_dict,
        'total_problems': total_problems
    }), 200

@problems_bp.route('/<problem_id>', methods=['GET'])
@token_required
def get_problem_by_id(current_user, problem_id):
    problem, error = problem_service.get_problem_full_details(problem_id)
    if error:
        return jsonify(error), 404
    return jsonify(problem), 200

@problems_bp.route('/<problem_id>/submit', methods=['POST'])
@token_required
def submit_problem(current_user, problem_id):
    data = request.get_json()
    code = data.get('code')
    language = data.get('language')

    if not code or not language:
        return jsonify({'error': 'Code and language are required.'}), 400

    submission = submission_service.handle_new_submission(problem_id, current_user['username'], language, code)

    if 'error' in submission:
        return jsonify({'error': submission['error']}), 500

    return jsonify(submission), 201
@problems_bp.route('/<problem_id>/meta', methods=['GET'])
@token_required
def get_problem_meta_by_id(current_user, problem_id):
    problem, error = problem_service.get_problem_by_id(problem_id)
    if error:
        return jsonify(error), 404
    
    return jsonify(problem), 200

@problems_bp.route('/<problem_id>/testcases', methods=['GET'])
@token_required
def get_problem_testcases(current_user, problem_id):
    testcases = judge_service.get_testcases(problem_id)
    if not testcases:
        return jsonify({"error": "No testcases found for this problem."}), 404
    return jsonify({"testcases": testcases}), 200