# DEFINE ALL APP ROUTES (used in views and for API)

from app import app

from app.routes.api import api
from app.routes.views import view, constants
from app.routes.admin import admin
from app.constants import ERROR_MESSAGES

from flask import request, render_template
from werkzeug.exceptions import HTTPException


# Error handler for all routes
@app.errorhandler(HTTPException)
def errorHandler(error):
	if request.path.startswith(api.url_prefix): # API route
		return {
			"error": ERROR_MESSAGES[error.code] if error.code in ERROR_MESSAGES else error.description
		}, error.code
	return render_template("error.html",
		**constants,
		title = error.code,
		errorCode = error.code,
		errorMessage = ERROR_MESSAGES[error.code] if error.code in ERROR_MESSAGES else error.description
	), error.code


app.register_blueprint(api)
app.register_blueprint(view)
