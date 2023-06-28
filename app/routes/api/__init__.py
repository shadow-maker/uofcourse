from flask import Blueprint, request
from werkzeug.exceptions import BadRequest

#
# Import all API routes (endpoints)
#

from app.routes.api.terms import *
from app.routes.api.grades import *
from app.routes.api.courses import *
from app.routes.api.subjects import *
from app.routes.api.faculties import *
from app.routes.api.me import *
from app.routes.api.announcements import *
from app.routes.api.counters import *

#
# Create API route blueprint with /api url prefix
#

api: Blueprint = Blueprint("api", __name__, url_prefix="/api")

#
# Register all sub-blueprints to the api blueprint
#

api.register_blueprint(term)
api.register_blueprint(course)
api.register_blueprint(subject)
api.register_blueprint(faculty)
api.register_blueprint(grade)
api.register_blueprint(me)
api.register_blueprint(announcement)
api.register_blueprint(counter)

#
# Validate API request
#

@api.before_request
def apiBeforeRequest():
	# Validate request data
	if request.content_length:
		try:
			if not request.is_json:
				raise BadRequest("Request data not in JSON format")
			request.json
		except BadRequest as e:
			return {"error": e.description}, 400

#
# Allow CORS
#

@api.after_request
def apiAfterRequest(response):
	response.headers["Access-Control-Allow-Origin"] = "*"
	return response
