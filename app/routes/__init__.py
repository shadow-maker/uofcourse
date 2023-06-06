# DEFINE ALL APP ROUTES (used in views and for API)

from app import app

from app import constants
from app.constants import ERROR_MESSAGES
from app.models import Role, Faculty
from app.routes.api import api
from app.routes.views import view
from app.routes.admin import admin
from app.routes.files import file

from flask import request, render_template
from werkzeug.exceptions import HTTPException


app.register_blueprint(api)
app.register_blueprint(view)
app.register_blueprint(file)

#
# Constants passed to all HTML templates to be accessed via Jinja2
#

@app.context_processor
def viewConstants():
	return {**{k : v for k, v in constants.__dict__.items() if not k.startswith("__")}, **{
		"DEBUG": app.debug,
		"GANALYTICS_ID" : app.config["GANALYTICS_ID"],
		"GADSENSE_ID" : app.config["GADSENSE_ID"],
		"PROPELLER_ID" : app.config["PROPELLER_ID"],
		"ROLE_ADMIN": Role.admin,
		"ROLE_MOD": Role.moderator,
		"FACULTIES": Faculty.query.all(),
	}}

#
# Error handler for all routes
#

@app.errorhandler(HTTPException)
def errorHandler(error):
	if request.path.startswith(api.url_prefix): # API route
		return {
			"error": ERROR_MESSAGES[error.code] if error.code in ERROR_MESSAGES else error.description
		}, error.code
	return render_template("error.html",
		title = error.code,
		errorCode = error.code,
		errorMessage = ERROR_MESSAGES[error.code] if error.code in ERROR_MESSAGES else error.description
	), error.code
