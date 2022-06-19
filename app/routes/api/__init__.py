from flask import Blueprint, request
from wtforms import ValidationError
from flask_wtf.csrf import validate_csrf

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

#
# Validate API request
#

@api.before_request
def apiBeforeRequest():
	# Validate AJAX Token
	token = request.headers.get("AJAX-TOKEN")
	if token:
		try:
			validate_csrf(token)
		except ValidationError as e:
			return {"error": str(e).replace("CSRF", "AJAX")}, 401
	else:
		return {"error": "Missing AJAX-TOKEN header"}, 401

	# Validate request data
	if request.content_length:
		try:
			if not request.is_json:
				raise BadRequest("Request data not in JSON format")
			request.json
		except BadRequest as e:
			return {"error": e.description}, 400
