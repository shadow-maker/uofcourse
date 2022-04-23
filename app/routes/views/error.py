from app.routes.views import view, constants

from flask import render_template

messages = {
	403: "You don't have permission to perform that action",
	404: "Page not found",
	500: "Server error"
}

@view.app_errorhandler(403)
@view.app_errorhandler(404)
@view.app_errorhandler(500)
def renderError(error):
	return render_template("error.html",
		**constants,
		title = error.code,
		errorCode = error.code,
		errorMessage = messages[error.code]
	), error.code