from flask_login import current_user
from planner import db
from planner.models import Faculty, Subject, Course
from planner.queryUtils import *
from planner.constants import *

from planner.routes.views import view

from flask import render_template, flash, redirect
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
		header = "Faculty",
		faculty = faculty
	)


@view.route("/s/<subjCode>")
@view.route("/c/<subjCode>")
def subject(subjCode):
	subject = getSubjectByCode(subjCode)
	if not subject:
		flash(f"Subject with code {subjCode} does not exist!", "danger")
		return redirect(url_for("view.home"))
	faculty = subject.faculty
	return render_template("subject.html",
		title=subjCode.upper(),
		header=f"Subject - {subject.name}",
		subject=subject,
		faculty=faculty,
		courses=subject.courses,
		backlinks={
			faculty.name: url_for("view.faculty", facId=faculty.id),
			subject.code: ""
		}.items()
	)


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
		title=f"{subjCode.upper()}-{courseCode.upper()}",
		course=course,
		subject=subject,
		faculty=faculty,
		userTags = course.getTags(current_user.id) if current_user.is_authenticated else [],
		userCourses = course.getUserCourses(current_user.id) if current_user.is_authenticated else [],
		colors = COLORS_DARK,
		links = {
			"faculty": url_for("view.faculty", facId=faculty.id),
			"subject": url_for("view.subject", subjCode=subject.code)
		}
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


@view.route("/c", methods=["GET", "POST"])
def courses():
	levels = {str(l) : True for l in COURSE_LEVELS}
	faculties = {
		str(f[0]) : {"name": f[1], "sel": True}
	for f in list(db.session.query(Faculty).values(Faculty.id, Faculty.name))}
	subjects = {
		s[0] : {"id": s[1], "name": s[2], "sel": False}
	for s in list(db.session.query(Subject).values(Subject.code, Subject.id, Subject.name))}
	subjects = {k : subjects[k] for k in sorted(subjects)}

	return render_template("coursesFilter.html",
		title = "Courses",
		header = f"Courses",
		sortOpt = 0,
		asc = True,
		colors = COLORS_DARK,
		terms = [dict(term) for term in Term.query.all()],
		filterData = {
			"levels": levels,
			"faculties": faculties,
			"subjects": subjects
		}
	)