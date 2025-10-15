from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
from extensions import mail, mongo
from flask_mail import Message

# from api.problems_api import problems_bp
# from api.users_api import users_bp
from api.auth_api import auth_bp
# from api.submissions_api import submissions_bp
# from api.contests_api import contests_api

def create_app():
    # import loggingme='app.log', level=logging.DEBUG)
    app = Flask(__name__)
    CORS(app)

    # Load environment variables
    load_dotenv()

    # Flask-Mail configuration
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587)) # Default to 587
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

    mail.init_app(app)

    # MongoDB configuration
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    mongo.init_app(app)

    # app.register_blueprint(problems_bp, url_prefix='/api/problems')
    # app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    # app.register_blueprint(submissions_bp, url_prefix='/api/submissions')
    # app.register_blueprint(contests_api, url_prefix='/api/contests')

    @app.route("/")
    def root():
        return {"message": "Backend is running!"}
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)