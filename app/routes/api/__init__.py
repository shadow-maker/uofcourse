from flask import Blueprint

#
# Create API route blueprint with /api url prefix
#

api: Blueprint = Blueprint("api", __name__, url_prefix="/api")

#
# Import all API routes (endpoints)
#

from app.routes.api.terms import *
from app.routes.api.grades import *
from app.routes.api.courses import *
from app.routes.api.subjects import *
from app.routes.api.faculties import *
from app.routes.api.me import *

#
# Register all sub-blueprints to the api blueprint
#

api.register_blueprint(term)
api.register_blueprint(course)
api.register_blueprint(subject)
api.register_blueprint(faculty)
api.register_blueprint(grade)
api.register_blueprint(me)
