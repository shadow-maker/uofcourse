from app.models import Faculty, Subject, Course
from app.auth import current_user
from app.constants import COURSE_LEVELS, REDDIT_URL
from app.routes.views import view

from flask import render_template, flash, redirect, request
from flask.helpers import url_for

from sqlalchemy.sql import func


@view.route("/c/<subjectCode>-<courseNumber>")
@view.route("/c/<subjectCode>/<courseNumber>")
def course(subjectCode, courseNumber):
	if not subjectCode.isupper():
		return redirect(url_for("view.course",
			subjectCode=subjectCode.upper(),
			courseNumber=courseNumber
		))
	subject = Subject.query.filter_by(code=subjectCode.upper()).first()
	if not subject:
		flash(f"Subject with code {subjectCode} does not exist!", "danger")
		return redirect(url_for("view.home"))
	course = Course.query.filter_by(subject_id=subject.id, number=courseNumber).first()
	if not course:
		flash(f"Course with code {subjectCode}-{courseNumber} does not exist!", "danger")
		return redirect(url_for("view.home"))

	userCourses = course.getUserCourses(current_user.id) if current_user.is_authenticated else []
	collections = current_user.collections if current_user.is_authenticated else []
	return render_template("course.html",
		title = f"{course.subject_code} {course.number}",
		description = f"Course info for {course.code} : {course.name}",
		course = course,
		subject = subject,
		faculty = subject.faculty,
		redditSearch = REDDIT_URL + "search/?q=" + course.code.replace("-", "%20"),
		userCourses = userCourses,
		collections = collections,
		hasCourse = lambda collection : bool(sum([uc.course_collection_id == collection.id for uc in userCourses]))
	)


@view.route("/c/id/<courseId>")
def courseById(courseId):
	course = Course.query.get(courseId)
	if not course:
		flash(f"Course with id {courseId} does not exist!", "danger")
		return redirect(url_for("view.home"))
	return redirect(url_for("view.course", subjectCode=course.subject.code, courseNumber=course.number))


@view.route("/c/random")
def courseRandom():
	course = Course.query.order_by(func.random()).first()
	return redirect(url_for("view.courseById", courseId=course.id))


@view.route("/c", methods=["GET"])
def courseBrowser():
	selSubject = request.args.get("subject")
	selFaculty = request.args.get("faculty")

	if selSubject:
		if not Subject.query.filter_by(code=selFaculty.upper()).first():
			flash(f"Subject with code {selSubject} does not exist!", "danger")
			return redirect(url_for("view.home"))
	if selFaculty:
		if not Faculty.query.get(selFaculty):
			flash(f"Faculty with id {selFaculty} does not exist!", "danger")
			return redirect(url_for("view.home"))

	levels = {str(l) : True for l in COURSE_LEVELS}

	faculties = {
		str(f[0]) : {"name": f[1], "sel": not selFaculty}
	for f in Faculty.query.with_entities(Faculty.id, Faculty.name)}

	if selFaculty:
		faculties[selFaculty]["sel"] = True

	subjects = {
		s[0] : {"id": s[1], "name": s[2], "sel": s[0] == selSubject}
	for s in list(Subject.query.with_entities(Subject.code, Subject.id, Subject.name))}

	subjects = {k : subjects[k] for k in sorted(subjects)}

	return render_template("courseBrowser.html",
		title = "Courses",
		header = "Course browser",
		headerIcon = "binoculars-fill",
		description = "Course browser : Filter and sort through UofC's full catalogue of courses",
		sortOpt = 0,
		sortOptions = [
			{"label": "Number", "value": ["number", "subject_code", "name"]},
			{"label": "Name", "value": ["name", "number", "subject_code"]},
		],
		collections = current_user.collections if current_user.is_authenticated else [],
		filterData = {
			"levels": levels,
			"faculties": faculties,
			"subjects": subjects
		}
	)


@view.route("/c/<subjectCode>")
def courseBrowserSubject(subjectCode):
	subject = Subject.query.filter_by(code=subjectCode.upper()).first()
	if not subject:
		flash(f"Subject with code {subjectCode} does not exist!", "danger")
		return redirect(url_for("view.home"))
	return redirect(url_for("view.courseBrowser", subject=subjectCode))
