from planner import db
from planner.models import Role, Season, Term, Grade, CourseCollection
from planner.models.utils import getAllYears
from planner.forms import formChangePassw
from planner.constants import *

from planner.routes.views import view
from planner.routes.views.utils import *
from planner.routes.api import *

from flask import render_template, flash, redirect, request
from flask.helpers import url_for
from flask_login import current_user


@view.route("/account", methods=["GET", "POST"])
def account():
	if not current_user.is_authenticated:
		return redirectLogin()
	
	formPassw = formChangePassw()

	if formPassw.validate_on_submit():
		if current_user.checkPassw(formPassw.oldPassw.data):
			try:
				current_user.updatePassw(formPassw.oldPassw.data, formPassw.newPassw.data)
				db.session.commit()
			except:
				flash(f"Error updating password!", "danger")
			else:
				flash(f"Password changed!", "success")
		else:
			flash(f"Current password is incorrect! - Password not changed", "danger")
	
	return render_template("account.html",
		title = "Account",
		header = "My Acccount",
		user = current_user,
		Role = Role,
		formPassw = formPassw
	)


@view.route("/my")
def planner():
	if not current_user.is_authenticated:
		return redirectLogin()
	
	return render_template("planner.html",
		title = "My Plan",
		header = "My Course Plan",
		userData = {
			"tags": current_user.tags,
			"collections": sorted(current_user.collections, key=lambda c: c.term_id if c.term_id else 0)
		},
		grades = Grade.query.all(),
		seasons = Season.query.all(),
		years = getAllYears(False)
	)


@view.route("/my/add/collection", methods=["POST"])
def addCourseCollection():
	def ret(message, category):
		flash(message, category)
		return redirect(url_for("view.planner"))

	if not current_user.is_authenticated:
		return ret("ERROR: User not logged in", "danger")

	data = request.form.to_dict()
	if not data:
		return ret("ERROR: No form data provided to add CourseCollection", "danger")

	if "term" in data:
		term = Term.query.filter_by(term_id=data["term"]).first()
	elif not (("season" in data) and ("year" in data)):
		return ret("ERROR: Term not specified", "danger")
	else:
		season = Season.query.filter_by(id=data["season"]).first()
		if not season:
			season = Season.query.filter_by(name=data["season"].lower()).first()
		if not season:
			return ret("ERROR: Season not found", "danger")
		term = Term.query.filter_by(season_id=season.id, year=data["year"]).first()

	if not term:
		return ret("ERROR: Term does not exist", "danger")

	if CourseCollection.query.filter_by(user_id=current_user.id, term_id=term.id).first():
		return ret(f"ERROR: User (#{current_user.id}) already has a collection for term {term.id}", "warning")

	db.session.add(CourseCollection(current_user.id, term.id))
	db.session.commit()
	return ret("Term added!", "success")


@view.route("/my/del/collection", methods=["DELETE", "POST"])
def delCourseCollection():
	def ret(message, category):
		flash(message, category)
		return redirect(url_for("view.planner"))

	if not current_user.is_authenticated:
		return ret("ERROR: User not logged in", "danger")

	data = request.form.to_dict()
	if not data:
		return ret("ERROR: No form data provided to remove CourseCollection", "danger")
	if not "id" in data:
		return ret("ERROR: No CourseCollection id provided", "danger")

	collection = CourseCollection.query.filter_by(id=data["id"]).first()

	if not collection:
		return ret(f"ERROR: CourseCollection does not exist!", "danger")

	if collection.user_id != current_user.id:
		return ret(f"ERROR: User (#{current_user.id}) does not have access to this CourseCollection", "danger")
	
	if collection.userCourses:
		return ret(f"ERROR: CourseCollection is not empty", "danger")

	db.session.delete(collection)
	db.session.commit()

	return ret(f"Term removed!", "success")


@view.route("/my/add/course", methods=["POST"])
def addUserCourse():
	response, _ = postUserCourse(request.form.to_dict())

	if "error" in response:
		flash(f"ERROR: {response['error']}", "danger")

	return redirect(url_for("view.planner"))


@view.route("my/course", methods=["POST"])
def modUserCourse():
	data = request.form.to_dict()
	if not data:
		flash("ERROR: No form data provided to remove UserCourse", "danger")
		return redirect(url_for("view.planner"))
	if not "method" in data:
		flash("ERROR: No method provided", "danger")
		return redirect(url_for("view.planner"))
	
	if data["method"] == "PUT":
		response, _ = putUserCourse(request.form.to_dict())
	elif data["method"] == "DELETE":
		response, _ = delUserCourse(request.form.to_dict())

	if "error" in response:
		flash(f"ERROR: {response['error']}", "danger")

	return redirect(url_for("view.planner"))
