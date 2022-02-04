from planner import app, db, loginManager, bcrypt
from planner.models import Course, User, Faculty, Season
from planner.forms import loginForm, registerForm
from planner.queryUtils import *
from planner.constants import *

from flask import render_template, flash, redirect, send_from_directory, request, jsonify, session
from flask.helpers import url_for
from flask_login import login_user, logout_user, current_user

import datetime as dt
from datetime import datetime, timedelta
import random
import json

SORT_OPTIONS = [
	[Course.code, Course.name],
	[Course.name, Course.code]
]

#
# Funcs
#

def redirectLogin():
	flash(f"You need to log in first!", "warning")
	return redirect(url_for("login"))

def redirectNoaccess():
	flash(f"You do not have permission to access this page!", "warning")
	return redirect(url_for("home"))

#
# Error pages
#

@app.errorhandler(404)
def pageNotFound(e):
	return render_template("error.html",
		title = "404",
		errorCode = 404,
		errorMessage = "Page not found"
	), 404

@app.errorhandler(403)
def pageNotFound(e):
	return render_template("error.html",
		title = "403",
		errorCode = 403,
		errorMessage = "You don't have permission to perform that action"
	), 403

@app.errorhandler(500)
def pageNotFound(e):
	return render_template("error.html",
		title = "404",
		errorCode = 500,
		errorMessage = "Server error"
	), 500


#
# UTILS
#

@loginManager.user_loader
def loadUser(uId):
	return User.query.get(int(uId))

#
# MAIN
#

@app.route("/home")
@app.route("/")
def home():
	return render_template("index.html", header="UofC Planner")


@app.route("/about")
def about():
	return render_template("about.html", title="About", header="About UofC Planner")

#
# AUTH
#

@app.route("/signup", methods=["GET", "POST"])
def signup():
	if current_user.is_authenticated:
		flash(f"You are already authenticated!", "success")
		return redirect(url_for("home"))
	form = registerForm()
	if form.validate_on_submit():
		if userExists(form.ucid.data):
			flash(f"User with UCID {form.ucid.data} already exist. Please sign in.", "danger")
		else:
			user = User(form.ucid.data, form.email.data, form.passw.data, form.fac.data)
			if form.name.data:
				user.name = form.name.data
			if form.entry.data:
				user.entryYear = form.entry.data
			db.session.add(user)
			db.session.commit()
			flash(f"Account created!", "success")
			return redirect(url_for("login"))
		return redirect(url_for("home"))
	return render_template("signup.html",
		title="Sign Up",
		header="Create Account",
		form=form
	)

@app.route("/login", methods=["GET", "POST"])
def login():
	if current_user.is_authenticated:
		flash(f"You are already authenticated!", "success")
		return redirect(url_for("home"))
	form = loginForm()
	if form.validate_on_submit():
		if not userExists(form.ucid.data):
			flash(f"User with UCID {form.ucid.data} doesn't exist. Please sign up for an account.", "danger")
		else:
			user = getById(User, form.ucid.data)
			if bcrypt.check_password_hash(user.passw, form.passw.data):
				login_user(user, remember=form.remember.data)
				flash(f"Log in successful! (#{user.id})", "success")
				return redirect(url_for("home"))
			else:
				flash(f"Incorrect password!", "danger")
	return render_template("login.html",
		title="Log In",
		header="Log In",
		form=form
	)

@app.route("/logout")
def logout():
	if not current_user.is_authenticated:
		return redirect(url_for("logout"))
	logout_user()
	return redirect(url_for("home"))

#
# ACCOUNT
#

@app.route("/account")
def account():
	if not current_user.is_authenticated:
		return redirectLogin()
	
	return render_template("account.html",
		title = "Account",
		header = "My acccount",
		user = dict(current_user)
	)

@app.route("/my")
def myPlanner():
	if not current_user.is_authenticated:
		return redirectLogin()

	return render_template("myPlanner.html",
		title = "My Plan",
		header = "My Course Plan",
		courseCollections = current_user.courseCollections,
		seasons = Season.query.all(),
		years = getAllYears(False)
	)

#
# COURSES
#

@app.route("/f/<facId>")
def facultyView(facId):
	faculty = getById(Faculty, facId)
	if not faculty:
		flash(f"Faculty with id {facId} does not exist!", "danger")
		return redirect(url_for("home"))
	return render_template("faculty.html",
		title = "Faculty",
		header = "Faculty",
		faculty = faculty
	)

@app.route("/c/filter", methods=["GET", "POST"])
def coursesFilter():
	sortOpt = 0
	sortBy = SORT_OPTIONS[sortOpt]

	levels = {str(l) : True for l in COURSE_LEVELS}
	faculties = {
		str(f[0]) : {"name": f[1], "sel": True}
	for f in list(db.session.query(Faculty).values(Faculty.id, Faculty.name))}
	subjects = {
		str(s[0]) : {"code": s[1], "sel": False}
	for s in list(db.session.query(Subject).values(Subject.id, Subject.code))}

	page = 1

	if request.method == "POST":
		if request.form:
			data = request.form
		elif request.json:
			data = request.json
		else:
			return jsonify({"error": "No data passed through json or form"})

		# Sort
		if "sortBy" in data:
			sortOpt = int(data["sortBy"]) if int(data["sortBy"]) in range(len(SORT_OPTIONS)) else 0
		sortBy = SORT_OPTIONS[sortOpt]
		
		if "orderBy" in data and data["orderBy"] != "asc":
			sortBy = [i.desc() for i in sortBy]

		# Filter

		if "selectedLevel" in data:
			for l in levels:
				levels[l] = l in data["selectedLevel"]
		
		if "selectedFaculty" in data:
			for f in faculties:
				faculties[f]["sel"] = f in data["selectedFaculty"]

		if "selectedSubject" in data:
			subjects = json.loads(data["selectedSubject"])

		if "subjectSearch" in data:
			subjSearch = getSubjectByCode(data["subjectSearch"])
			if subjSearch:
				subjects[str(subjSearch.id)]["sel"] = True
		
		if "page" in data:
			page = int(data["page"])

	levelIds = [l for l, sel in levels.items() if sel]

	facIds = [int(f) for f, v in faculties.items() if v["sel"]]

	subjIds = [s for s in subjects if subjects[s]["sel"]]
	if not subjIds:
		subjIds = [s[0] for s in list(db.session.query(Subject).values(Subject.id))]
	subjIds = [s for s in subjIds if Subject.query.filter_by(id=s).first().faculty_id in facIds]

	query = Course.query.filter(Course.level.in_(levelIds), Course.subject_id.in_(subjIds)).order_by(*sortBy)

	results = query.paginate(per_page=30, page=page)

	courses = [{
		"id": course.id,
		"name": course.name,
		"subj": course.subject.code,
		"code": course.code,
		"emoji": course.getEmoji(128218),
	} for course in results.items]

	return jsonify({
		"subjects": subjects,
		"courses": courses,
		"page": page,
		"pages": results.pages,
		"total": results.total
	})

@app.route("/c", methods=["GET", "POST"])
def allCoursesView():
	sortOpt = 0
	sortBy = SORT_OPTIONS[0]
	asc = True

	levels = {str(l) : True for l in COURSE_LEVELS}
	faculties = {
		str(f[0]) : {"name": f[1], "sel": True}
	for f in list(db.session.query(Faculty).values(Faculty.id, Faculty.name))}
	subjects = {
		str(s[0]) : {"code": s[1], "sel": False}
	for s in list(db.session.query(Subject).values(Subject.id, Subject.code))}

	page = 1

	""" Not longer used since form moved to AJAX:
	form = request.form
	if form:
		# Sort
		sortOpt = int(form.get("sortBy")) if int(form.get("sortBy")) in range(len(SORT_OPTIONS)) else 0
		sortBy = SORT_OPTIONS[sortOpt]
	
		if form.get("orderBy") != "asc":
			sortBy = [i.desc() for i in sortBy]
			asc = False

		# Filter
		selectedLevel = form.getlist("selectedLevel")
		for l in levels:
			levels[l] = l in selectedLevel
		
		selectedFaculty = form.getlist("selectedFaculty")
		for f in faculties:
			faculties[f]["sel"] = f in selectedFaculty

		selectedSubject = form.getlist("selectedSubject")
		for s in subjects:
			subjects[s]["sel"] = s in selectedSubject

		subjSearch = getSubjectByCode(form.get("subjectSearch"))
		if subjSearch:
			subjects[str(subjSearch.id)]["sel"] = True
	
		# Pagination
		page = int(form.get("page"))
	"""

	levelIds = [l for l, sel in levels.items() if sel]

	facIds = [int(f) for f, data in faculties.items() if data["sel"]]

	subjIds = [s for s in subjects if subjects[s]["sel"]]
	if not subjIds:
		subjIds = [s[0] for s in list(db.session.query(Subject).values(Subject.id))]
	subjIds = [s for s in subjIds if Subject.query.filter_by(id=s).first().faculty_id in facIds]

	query = Course.query.filter(Course.level.in_(levelIds), Course.subject_id.in_(subjIds)).order_by(*sortBy)

	results = query.paginate(per_page=30, page=page)

	courses = [{
		"id": course.id,
		"name": course.name,
		"subj": course.subject.code,
		"code": course.code,
		"emoji": course.getEmoji(128218),
	} for course in results.items]
	
	return render_template("coursesFilter.html",
		title = "Courses",
		header = f"Courses",
		sortOpt = sortOpt,
		asc = asc,
		filterData = {
			"levels": levels,
			"faculties": faculties,
			"subjects": subjects
		},
		results = {
			"courses": courses,
			"page": page,
			"pages": results.pages,
			"total": results.total,
		}
	)

#@app.route("/c")
#def allCoursesViewAlt():
#	return redirect(url_for("allCoursesView"))


@app.route("/c/id/<courseId>")
def courseById(courseId):
	course = getById(Course, courseId)
	if not course:
		flash(f"Course with id {courseId} does not exist!", "danger")
		return redirect(url_for("home"))
	return redirect(url_for("courseView", subjCode=course.subject.code, courseCode=course.code))


@app.route("/c/random")
def courseRandom():
	course = None
	while not course:
		course = Course.query[random.randrange(0, Course.query.count())]
	return redirect(url_for("courseById", courseId=course.id))


@app.route("/c/<subjCode>")
def subjectView(subjCode):
	subject = getSubjectByCode(subjCode)
	if not subject:
		flash(f"Subject with code {subjCode} does not exist!", "danger")
		return redirect(url_for("home"))
	print("OK")
	#return redirect(url_for("allCoursesView", subject=subject.code))
	faculty = subject.faculty
	return render_template("subject.html",
		title=subjCode,
		header=f"Subject - {subject.name}",
		subject=subject,
		faculty=faculty,
		courses=subject.courses,
		backlinks={
			faculty.name: url_for("facultyView", facId=faculty.id),
			subject.code: ""
		}.items()
	)


@app.route("/c/<subjCode>/<courseCode>")
def courseView(subjCode, courseCode):
	subject = getSubjectByCode(subjCode)
	if not subject:
		flash(f"Subject with code {subjCode} does not exist!", "danger")
		return redirect(url_for("home"))
	course = getCourseById(subject.id, courseCode)
	if not course:
		flash(f"Course with code {subjCode}-{courseCode} does not exist!", "danger")
		return redirect(url_for("home"))
	faculty = subject.faculty
	return render_template("course.html",
		title=f"{subjCode}-{courseCode}",
		course=course,
		subject=subject,
		faculty=faculty,
		backlinks={
			faculty.name: url_for("facultyView", facId=faculty.id),
			subject.code: url_for("subjectView", subjCode=subject.code),
			course.code: ""
		}.items()
	)
