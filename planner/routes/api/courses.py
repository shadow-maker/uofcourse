from planner import db
from planner.models import Course, Subject, Faculty
from planner.routes.api.utils import *

from flask import Blueprint, request
from flask_login import current_user
from sqlalchemy import func, and_, or_

course = Blueprint("courses", __name__, url_prefix="/courses")


#
# GET
#

@course.route("", methods=["GET"])
def getCourses(search="", levels=[], subjects=[], faculties=[], repeat=None, nogpa=None):
	# Parse search
	if not search:
		search = request.args.get("search", default="", type=str)
	search = search.strip().lower()

	# Parse levels
	try:
		if not levels: # levels not passed as function argument
			levels = request.args.getlist("levels", type=int)
		if not levels: # levels not passed as url argument
			levels = COURSE_LEVELS
		else: # check if levels are valid
			for l in levels:
				if int(l) not in COURSE_LEVELS:
					return {"error": f"Invalid level {l}"}, 400
	except:
		return {"error": "Could not parse levels, invalid format"}, 400

	# Parse subjects
	try:
		if not subjects: # subjects not passed as function argument
			subjects = request.args.getlist("subjects", type=str)
		if not subjects: # subjects not passed as url argument
			subjects = [s[0] for s in list(db.session.query(Subject).with_entities(Subject.id))]
		else: # check if subjects are valid
			for i, s in enumerate(subjects):
				if s.isdigit():
					if not utils.getById(Subject, s):
						return {"error": f"Invalid subject {s}"}, 400
				elif utils.getSubjectByCode(s).first():
					subjects[i] = utils.getSubjectByCode(s).id
				else:
					return {"error": f"Invalid subject {s}"}, 400
	except:
		return {"error": "Could not parse subjects, invalid format"}, 400

	# Parse faculties
	try:
		if not faculties: # faculties not passed as function argument
			faculties = request.args.getlist("faculties", type=int)
		if not faculties: # faculties not passed as url argument
			faculties = [f[0] for f in list(db.session.query(Faculty).with_entities(Faculty.id))]
		else: # check if faculties are valid
			for f in faculties:
				if not utils.getById(Faculty, f):
					return {"error": f"Invalid faculty {f}"}, 400
	except:
		return {"error": "Could not parse faculties, invalid format"}, 400
	
	# Parse repeat
	if repeat == None:
		repeat = request.args.get("repeat", default="false", type=str).lower()
	if type(repeat) != bool and repeat not in ["true", "1", "false", "0"]:
		return {"error": f"'{repeat}' is not a valid value for repeat (boolean)"}, 400
	repeat = repeat in [True, "true", "1"]

	# Parse nogpa
	if nogpa == None:
		nogpa = request.args.get("nogpa", default="false", type=str).lower()
	if type(nogpa) != bool and nogpa not in ["true", "1", "false", "0"]:
		return {"error": f"'{nogpa}' is not a valid value for nogpa (boolean)"}, 400
	nogpa = nogpa in [True, "true", "1"]

	# Convert levels list into a list of tuples where each tuple is a range of levels
	levelsFilter = []
	for l in levels:
		if levelsFilter and levelsFilter[-1][1] == l:
			levelsFilter[-1][1] = l + 1
		else:
			levelsFilter.append([l, l + 1])
	
	# Remove subjects that are not in the selected faculties
	subjectsFilter = []
	for s in subjects:
		if Subject.query.filter(Subject.id == s, Subject.faculty_id.in_(faculties)).first():
			subjectsFilter.append(s)
	
	# Filters tuple to check that the course is in the selected levels and subjects
	filters = (
		or_(and_(Course.number >= l[0] * 100, Course.number < l[1] * 100) for l in levelsFilter),
		Course.subject_id.in_(subjectsFilter),
		Course.repeat == repeat,
		Course.nogpa == nogpa,
		Course.name.ilike(f"%{search}%")
	)

	# Serializer function to convert a Course object into a JSON-serializable dictionary
	def serializer(course):
		data = dict(course)
		data["emoji"] = course.getEmoji()
		if current_user.is_authenticated:
			data["tags"] = [tag.id for tag in course.userTags if tag.user_id == current_user.id]
			data["collections"] = [dict(uc.collection) for uc in course.getUserCourses(current_user.id)]
		return data
	
	# Get results
	return getAll(Course, filters, serializer)


@course.route("/<id>", methods=["GET"])
def getCourseById(id):
	return getById(Course, id)


@course.route("/code/<subjectCode>/<courseNumber>", methods=["GET"])
def getCourseByCode(subjectCode, courseNumber):
	subject = utils.getSubjectByCode(subjectCode)
	if not subject:
		return {"error": f"Subject with code {subjectCode} does not exist"}, 404
	course = Course.query.filter_by(subject_id=subject.id, number=courseNumber).first()
	if not course:
		return {"error": f"Course with code {subjectCode}-{courseNumber} does not exist"}, 404
	return dict(course)
