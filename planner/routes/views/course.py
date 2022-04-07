from flask_login import current_user
from planner import db
from planner.models import Faculty, Subject, Course
from planner.models.utils import getSubjectByCode
from planner.constants import *

from planner.routes.views import view

from flask import render_template, flash, redirect, request
from flask.helpers import url_for

import random


@view.route("/f/<facId>")
def faculty(facId):
	faculty = Faculty.query.get(facId)
	if not faculty:
		flash(f"Faculty with id {facId} does not exist!", "danger")
		return redirect(url_for("view.home"))
	return render_template("faculty.html",
		title = "Faculty",
		description = f"Faculty info for {faculty.name}",
		faculty = faculty,
		lenSubjects=len(faculty.subjects),
		lenCourses = sum([len(s.courses) for s in faculty.subjects]),
		subjects = [{
			"id": s.id,
			"emoji": s.getEmoji(),
			"code": s.code,
			"name": s.name,
			"url": s.url
		} for s in faculty.subjects],
	)


@view.route("/s/<subjectCode>")
def subject(subjectCode):
	subject = getSubjectByCode(subjectCode)
	if not subject:
		flash(f"Subject with code {subjectCode} does not exist!", "danger")
		return redirect(url_for("view.home"))
	faculty = subject.faculty
	return render_template("subject.html",
		title = subjectCode.upper(),
		description = f"Subject info for {subject.code} : {subject.name}",
		subject = subject,
		faculty = faculty,
		lenCourses = len(subject.courses)
	)


@view.route("/c/<subjectCode>")
def courseBrowserSubject(subjectCode):
	subject = getSubjectByCode(subjectCode)
	if not subject:
		flash(f"Subject with code {subjectCode} does not exist!", "danger")
		return redirect(url_for("view.home"))
	return redirect(url_for("view.courseBrowser", subject=subjectCode))


@view.route("/c/<subjectCode>/<courseNumber>")
def course(subjectCode, courseNumber):
	subject = getSubjectByCode(subjectCode)
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
		title = f"{course.code}",
		description = f"Course info for {course.code} : {course.name}",
		course = course,
		subject = subject,
		faculty = subject.faculty,
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
		if not Faculty.query.get(selFaculty):
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
			{"label": "Number", "value": ["number", "name"]},
			{"label": "Name", "value": ["name", "number"]},
		],
		collections = current_user.collections if current_user.is_authenticated else [],
		filterData = {
			"levels": levels,
			"faculties": faculties,
			"subjects": subjects
		}
	)
