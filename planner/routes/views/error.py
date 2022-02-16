from planner.routes.views import view

from flask import render_template


@view.app_errorhandler(404)
def pageNotFound(e):
	print(e)
	print(type(e))
	print(dir(e))
	return render_template("error.html",
		title = "404",
		errorCode = 404,
		errorMessage = "Page not found"
	), 404

@view.app_errorhandler(403)
def pageNotFound(e):
	return render_template("error.html",
		title = "403",
		errorCode = 403,
		errorMessage = "You don't have permission to perform that action"
	), 403

@view.app_errorhandler(500)
def pageNotFound(e):
	return render_template("error.html",
		title = "404",
		errorCode = 500,
		errorMessage = "Server error"
	), 500