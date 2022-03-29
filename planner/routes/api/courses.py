from planner import db
from planner.models import Course, Subject, Faculty
from planner.routes.api.utils import *

from flask import Blueprint, request
from flask_login import current_user
from sqlalchemy import and_, or_

import json

course = Blueprint("courses", __name__, url_prefix="/courses")


#
# GET
#

@course.route("", methods=["GET"])
def getCourses():
	return getAll(Course)


@course.route("/<id>", methods=["GET"])
def getCourseById(id):
	return getById(Course, id)


@course.route("/code/<subjCode>/<courseCode>", methods=["GET"])
def getCourseByCode(subjCode, courseCode):
	subject = utils.getSubjectByCode(subjCode)
	if not subject:
		return {"error": f"Subject with code {subjCode} does not exist"}, 404
	course = Course.query.filter_by(subject_id=subject.id, code=courseCode).first()
	if not course:
		return {"error": f"Course with code {subjCode}-{courseCode} does not exist"}, 404
	return dict(course)


@course.route("/filter", methods=["GET"])
def getCoursesFilter(levels=[], subjects=[], faculties=[]):
	try:
		if not levels: # levels not passed as function argument
			levels = request.args.getlist("levels" + "[]", type=int)
		if not levels: # levels not passed as url argument
			levels = COURSE_LEVELS
		else: # check if levels are valid
			for l in levels:
				if int(l) not in COURSE_LEVELS:
					return {"error": f"Invalid level {l}"}, 400
	except:
		return {"error": "Could not parse levels, invalid format"}, 400

	try:
		if not faculties: # faculties not passed as function argument
			faculties = request.args.getlist("faculties" + "[]", type=int)
		if not faculties: # faculties not passed as url argument
			faculties = [f[0] for f in list(db.session.query(Faculty).with_entities(Faculty.id))]
		else: # check if faculties are valid
			for f in faculties:
				if not Faculty.query.filter_by(id=f).first():
					return {"error": f"Invalid faculty {f}"}, 400
	except:
		return {"error": "Could not parse faculties, invalid format"}, 400

	try:
		if not subjects: # subjects not passed as function argument
			subjects = request.args.getlist("subjects" + "[]", type=str)
		if not subjects: # subjects not passed as url argument
			subjects = [s[0] for s in list(db.session.query(Subject).with_entities(Subject.id))]
		else: # check if subjects are valid
			for i, s in enumerate(subjects):
				if s.isdigit():
					if not Subject.query.filter_by(id=s):
						return {"error": f"Invalid subject {s}"}, 400
				elif utils.getSubjectByCode(s).first():
					subjects[i] = utils.getSubjectByCode(s).id
				else:
					return {"error": f"Invalid subject {s}"}, 400
	except:
		return {"error": "Could not parse subjects, invalid format"}, 400

	levelsFilter = []
	for l in levels:
		if levelsFilter and levelsFilter[-1][1] == l:
			levelsFilter[-1][1] = l + 1
		else:
			levelsFilter.append([l, l + 1])
	
	subjectsFilter = []
	for s in subjects:
		if Subject.query.filter(Subject.id == s, Subject.faculty_id.in_(faculties)).first():
			subjectsFilter.append(s)
	
	filters = (
		or_(and_(Course.code >= l[0] * 100, Course.code < l[1] * 100) for l in levelsFilter),
		Course.subject_id.in_(subjectsFilter)
	)

	def serializer(course):
		return {
			"id": course.id,
			"name": course.name,
			"subject_id": course.subject_id,
			"code": course.code,
			"code_full": course.code_full,
			"emoji": course.getEmoji(),
			"url": course.url,
			"tags": [tag.id for tag in course.userTags if tag.user_id == current_user.id] if current_user.is_authenticated else [],
			"collections": [dict(uc.collection) for uc in course.getUserCourses(current_user.id)] if current_user.is_authenticated else []
		}
	
	return getAll(Course, filters, serializer)
