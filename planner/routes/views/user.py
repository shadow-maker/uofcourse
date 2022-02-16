from planner import db
from planner.queryUtils import *
from planner.constants import *

from planner.routes.views import view
from planner.routes.utils import *
from planner.routes.api import *

from flask import render_template, flash, redirect, request
from flask.helpers import url_for
from flask_login import current_user


@view.route("/account")
def viewAccount():
	if not current_user.is_authenticated:
		return redirectLogin()
	
	return render_template("account.html",
		title = "Account",
		header = "My acccount",
		user = dict(current_user)
	)

@view.route("/my")
def viewMyPlanner():
	if not current_user.is_authenticated:
		return redirectLogin()
	
	return render_template("myPlanner.html",
		title = "My Plan",
		header = "My Course Plan",
		courseCollections = sorted(current_user.collections, key=lambda c: c.term_id if c.term_id else 0),
		grades = Grade.query.all(),
		seasons = Season.query.all(),
		years = getAllYears(False)
	)

@view.route("/my/add/collection", methods=["POST"])
def addCourseCollection():
	def ret(message, category):
		flash(message, category)
		return redirect(url_for("view.viewMyPlanner"))

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
		return ret(f"ERROR: User (#{current_user.ucid}) already has a collection for term {term.id}", "warning")

	db.session.add(CourseCollection(current_user.id, term.id))
	db.session.commit()
	return ret("Term added!", "success")



@view.route("/my/del/collection", methods=["DELETE", "POST"])
def delCourseCollection():
	def ret(message, category):
		flash(message, category)
		return redirect(url_for("view.viewMyPlanner"))

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
		return ret(f"ERROR: User (#{current_user.ucid}) does not have access to this CourseCollection", "danger")
	
	if collection.userCourses:
		return ret(f"ERROR: CourseCollection is not empty", "danger")

	db.session.delete(collection)
	db.session.commit()

	flash(f"Term removed!", "success")

	return redirect(url_for("view.viewMyPlanner"))


@view.route("/my/edit/course", methods=["PUT", "POST"])
def editUserCourse():
	response, _ = apiEditUserCourse(request.form.to_dict())

	if "error" in response:
		flash(f"ERROR: {response['error']}", "danger")

	return redirect(url_for("view.viewMyPlanner"))
