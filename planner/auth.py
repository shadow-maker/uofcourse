from planner import loginManager
from planner.models import User

from flask import flash, redirect, request
from flask.helpers import url_for
from flask_login import current_user, login_user, logout_user, login_required
from flask_login.utils import login_url

from functools import wraps

loginManager.login_view = "view.login"
loginManager.login_message = "You need to log in first!"

loginManager.user_loader(lambda uid: User.query.get(uid))

@loginManager.unauthorized_handler
def unauthorized():
	if request.blueprint.split(".")[0] == "api":
		return {"error": "User not logged in"}, 401
	else:
		flash(loginManager.login_message, loginManager.login_message_category)
		return redirect(login_url(loginManager.login_view, next_url=request.url))

def role_required(role):
	def decorator(f):
		@wraps(f)
		@login_required
		def decorated_function(*args, **kwargs):
			if current_user.role < role:
				flash(f"You do not have permission to access this page!", "danger")
				return redirect(url_for("view.home"))
			return f(*args, **kwargs)
		return decorated_function
	return decorator
