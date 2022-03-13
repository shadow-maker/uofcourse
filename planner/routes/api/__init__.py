from flask import Blueprint
api = Blueprint("api", __name__, url_prefix="/api")

from planner.routes.api.terms import *
from planner.routes.api.grades import *
from planner.routes.api.courses import *
from planner.routes.api.subjects import *
from planner.routes.api.faculties import *
from planner.routes.api.seasons import *
from planner.routes.api.users import *
from planner.routes.api.tags import *

api.register_blueprint(season)
api.register_blueprint(term)
api.register_blueprint(course)
api.register_blueprint(subject)
api.register_blueprint(faculty)
api.register_blueprint(grade)
api.register_blueprint(user)
api.register_blueprint(tag)