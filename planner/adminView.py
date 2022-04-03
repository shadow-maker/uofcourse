from planner import app, db
from planner.models import User, Grade, Course, Subject, Faculty, Term, Season

from flask import redirect, flash
from flask.helpers import url_for
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

class adminModelView(ModelView):
	def is_accessible(self):
		return current_user.is_authenticated and current_user.isAdmin()

	def inaccessible_callback(self, name, **kwargs):
		if current_user.is_authenticated:
			flash(f"You do not have permission to access this page!", "warning")
			return redirect(url_for("view.home"))
		flash(f"You need to log in first!", "warning")
		return redirect(url_for("view.login"))

class adminIndexView(AdminIndexView):
	def is_accessible(self):
		return current_user.is_authenticated and current_user.isAdmin()

	def inaccessible_callback(self, name, **kwargs):
		if current_user.is_authenticated:
			flash(f"You do not have permission to access this page!", "warning")
			return redirect(url_for("view.home"))
		flash(f"You need to log in first!", "warning")
		return redirect(url_for("view.login"))

admin = Admin(app, name="UofC Planner", template_mode="bootstrap3", index_view=adminIndexView())

admin.add_view(adminModelView(User, db.session))
admin.add_view(adminModelView(Grade, db.session))
admin.add_view(adminModelView(Course, db.session))
admin.add_view(adminModelView(Subject, db.session))
admin.add_view(adminModelView(Faculty, db.session))
admin.add_view(adminModelView(Term, db.session))
admin.add_view(adminModelView(Season, db.session))
