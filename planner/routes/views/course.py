from flask_login import current_user
from planner import db
from planner.models import Faculty, Subject, Course
from planner.queryUtils import *
from planner.constants import *

from planner.routes.views import view

from flask import render_template, flash, redirect, request
from flask.helpers import url_for

import random


@view.route("/f/<facId>")
def faculty(facId):
	faculty = getById(Faculty, facId)
	if not faculty:
		flash(f"Faculty with id {facId} does not exist!", "danger")
		return redirect(url_for("view.home"))
	return render_template("faculty.html",
		title = "Faculty",
		faculty = faculty,
		lenSubjects=len(faculty.subjects),
		lenCourses = sum([len(s.courses) for s in faculty.subjects])
	)


@view.route("/s/<subjCode>")
def subject(subjCode):
	subject = getSubjectByCode(subjCode)
	if not subject:
		flash(f"Subject with code {subjCode} does not exist!", "danger")
		return redirect(url_for("view.home"))
	faculty = subject.faculty
	return render_template("subject.html",
		title=subjCode.upper(),
		subject=subject,
		faculty=faculty,
		lenCourses=len(subject.courses)
	)


@view.route("/c/<subjCode>")
def courseBrowserSubject(subjCode):
	subject = getSubjectByCode(subjCode)
	if not subject:
		flash(f"Subject with code {subjCode} does not exist!", "danger")
		return redirect(url_for("view.home"))
	return redirect(url_for("view.courseBrowser", subject=subjCode))


@view.route("/c/<subjCode>/<courseCode>")
def course(subjCode, courseCode):
	subject = getSubjectByCode(subjCode)
	if not subject:
		flash(f"Subject with code {subjCode} does not exist!", "danger")
		return redirect(url_for("view.home"))
	course = Course.query.filter_by(subject_id=subject.id, code=courseCode).first()
	if not course:
		flash(f"Course with code {subjCode}-{courseCode} does not exist!", "danger")
		return redirect(url_for("view.home"))
	faculty = subject.faculty
	return render_template("course.html",
		title=f"{course.code_full}",
		description = f"Course info for {course.code_full} : {course.name}",
		course=course,
		subject=subject,
		faculty=faculty,
		userTags = course.getTags(current_user.id) if current_user.is_authenticated else [],
		userCourses = course.getUserCourses(current_user.id) if current_user.is_authenticated else []
	)


@view.route("/c/id/<courseId>")
def courseById(courseId):
	course = getById(Course, courseId)
	if not course:
		flash(f"Course with id {courseId} does not exist!", "danger")
		return redirect(url_for("view.home"))
	return redirect(url_for("view.course", subjCode=course.subject.code, courseCode=course.code))


@view.route("/c/random")
def courseRandom():
	course = None
	while not course:
		course = Course.query[random.randrange(0, Course.query.count())]
	return redirect(url_for("view.courseById", courseId=course.id))


@view.route("/c", methods=["GET"])
def courseBrowser():
	selSubject = request.args.get("subject")
	selFaculty = request.args.get("faculty")

	if selSubject:
		if not getSubjectByCode(selSubject):
			flash(f"Subject with code {selSubject} does not exist!", "danger")
			return redirect(url_for("view.home"))
	if selFaculty:
		if not getById(Faculty, selFaculty):
			flash(f"Faculty with id {selFaculty} does not exist!", "danger")
			return redirect(url_for("view.home"))

	levels = {str(l) : True for l in COURSE_LEVELS}

	faculties = {
		str(f[0]) : {"name": f[1], "sel": not selFaculty}
	for f in list(db.session.query(Faculty).values(Faculty.id, Faculty.name))}

	if selFaculty:
		faculties[selFaculty]["sel"] = True

	subjects = {
		s[0] : {"id": s[1], "name": s[2], "sel": s[0] == selSubject}
	for s in list(db.session.query(Subject).values(Subject.code, Subject.id, Subject.name))}

	subjects = {k : subjects[k] for k in sorted(subjects)}

	return render_template("courseBrowser.html",
		title = "Courses",
		header = f"Course browser",
		description = "Course browser : Filter and sort through UofC's full catalogue of courses",
		sortOpt = 0,
		sortOptions = [
			{"label": "Course number", "value": ["code", "name"]},
			{"label": "Course name", "value": ["name", "code"]},
		],
		terms = [dict(term) for term in Term.query.all()],
		filterData = {
			"levels": levels,
			"faculties": faculties,
			"subjects": subjects
		}
	)