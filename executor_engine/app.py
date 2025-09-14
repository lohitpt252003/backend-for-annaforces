from flask import Flask, request, jsonify
from flask_cors import CORS
from execute import execute_code

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return "Code Execution API is running"

@app.route('/api/execute', methods=['POST'])
def execute():
    data = request.get_json()
    code = data.get('code')
    language = data.get('language')
    stdin = data.get('stdin', '')
    timelimit = data.get('timelimit', 2) # Default to 2 seconds
    memorylimit = data.get('memorylimit', 1024) # Default to 1024 MB

    if not code or not language:
        return jsonify({'error': 'Code and language are required.'}), 400

    result = execute_code(
        language=language,
        code=code,
        stdin=stdin,
        time_limit_s=timelimit,
        memory_limit_mb=memorylimit
    )

    return jsonify(result)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
