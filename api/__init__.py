from .auth_api import auth_bp
from .problems_api import problems_bp
from .submissions_api import submissions_bp
from .users_api import users_bp
from .contests_api import contests_api

__all__ = [
    'auth_bp',
    'problems_bp',
    'submissions_bp',
    'users_bp',
    'contests_api'
]
