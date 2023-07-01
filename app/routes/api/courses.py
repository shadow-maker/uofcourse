from app.models import Term, Course, Subject, Faculty
from app.auth import current_user, login_required
from app.routes.api.utils import *

from flask import Blueprint, request


course = Blueprint("courses", __name__, url_prefix="/courses")


#
# GET
#

@course.route("", methods=["GET"])
def getCourses(name="", numbers=[], levels=[], faculties=[], subjects=[], repeat=None, countgpa=None, old=None):
	# Parse name search query
	try:
		if not name:
			name = request.args.get("name", default="", type=str)
		name = name.strip().lower()
	except:
		return {"error": "Could not parse name, invalid format"}, 400

	# Parse numbers
	try:
		if not numbers:
			numbers = list(dict.fromkeys(request.args.getlist("number", type=int)))
		for n in numbers: # check if numbers are valid
			if n < min(COURSE_LEVELS) * 100 or n >= (max(COURSE_LEVELS) + 1) * 100:
				return {"error": f"Invalid course number {n}"}, 400
	except:
		return {"error": "Could not parse numbers, invalid format"}, 400

	# Parse levels
	try:
		if not levels: # levels not passed as function argument
			levels = list(dict.fromkeys(request.args.getlist("level", type=int)))
		for l in levels: # check if levels are valid
			if l not in COURSE_LEVELS:
				return {"error": f"Invalid level {l}"}, 400
	except:
		return {"error": "Could not parse levels, invalid format"}, 400

	# Parse faculties
	try:
		if not faculties: # faculties not passed as function argument
			faculties = list(dict.fromkeys(request.args.getlist("faculty", type=int)))
		for f in faculties: # check if faculties are valid
			if not Faculty.query.get(f):
				return {"error": f"Invalid faculty {f}"}, 400
	except:
		return {"error": "Could not parse faculties, invalid format"}, 400

	# Parse subjects
	try:
		if not subjects: # subjects not passed as function argument
			subjects = list(dict.fromkeys(request.args.getlist("subject", type=str)))
		if not subjects: # subjects not passed as url argument
			subjects = [s[0] for s in Subject.query.filter(
				*([Subject.faculty_id.in_(faculties)] if faculties else [])
			).with_entities(Subject.id)]
		else:
			for s in subjects[:]: # check if subjects are valid
				subject = Subject.query.get(s) if s.isdigit() else Subject.query.filter_by(code=s.upper()).first()
				if subject:
					# Only select subjects that belong to one of the passed faculties
					if faculties and not subject.faculty_id in faculties:
						subjects.remove(s)
					else:
						subjects[subjects.index(s)] = subject.id
				else:
					return {"error": f"Invalid subject {s}"}, 400
	except:
		return {"error": "Could not parse subjects, invalid format"}, 400

	# Parse repeat
	if repeat is None:
		repeat = request.args.get("repeat", type=str)
	if repeat is not None:
		if type(repeat) == str:
			repeat = repeat.lower()
		if type(repeat) != bool and repeat not in ["true", "1", "false", "0"]:
			return {"error": f"'{repeat}' is not a valid value for repeat (boolean)"}, 400
		repeat = repeat in [True, "true", "1"]

	# Parse countgpa
	if countgpa is None:
		countgpa = request.args.get("countgpa", type=str)
	if countgpa is not None:
		if type(countgpa) == str:
			countgpa = countgpa.lower()
		if type(countgpa) != bool and countgpa not in ["true", "1", "false", "0"]:
			return {"error": f"'{countgpa}' is not a valid value for countgpa (boolean)"}, 400
		countgpa = countgpa in [True, "true", "1"]

	# Parse old
	if old is None:
		old = request.args.get("old", type=str)
	if old is not None:
		if type(old) == str:
			old = old.lower()
		if type(old) != bool and old not in ["true", "1", "false", "0"]:
			return {"error": f"'{old}' is not a valid value for countgpa (boolean)"}, 400
		old = old in [True, "true", "1"]
	
	# Filters
	filters = [
		Course.name.ilike(f"%{name}%"),
		Course.subject_id.in_(subjects)
	]
	if numbers:
		filters.append(Course.number.in_(numbers))
	if levels:
		filters.append(Course.level.in_(levels))
	if repeat is not None:
		filters.append(Course.repeat == repeat)
	if countgpa is not None:
		filters.append(Course.countgpa == countgpa)
	if old is not None:
		filters.append(Course.old == old)

	# Serializer function to convert a Course object into a JSON-serializable dictionary
	def serializer(course):
		data = dict(course)
		if current_user.is_authenticated:
			data["tags"] = [tag.id for tag in course.tags if tag.user_id == current_user.id]
			data["collections"] = [cc.collection.id for cc in course.getCollectionCourses(current_user.id)]
		return data
	
	# Get results
	return getAll(Course, tuple(filters), serializer)


@course.route("/<id>", methods=["GET"])
def getCourseById(id):
	return getById(Course, id)

@course.route("/<id>/ratings", methods=["GET"])
@login_required
def getCourseRatings(id):
	course = Course.query.get(id)
	if not course:
		return {"error": f"Course with id {id} does not exist"}, 404
	outof = request.args.get("outof", default=100, type=int)
	decimals = request.args.get("decimals", default=0, type=int)
	termId = request.args.get("term", default=None, type=int)
	term = None
	if termId is not None:
		term = Term.query.get(termId)
		if not term:
			return {"error": f"Provided term id {termId} does not exist"}, 404
		if term not in course.calendar_terms:
			return {"error": f"Course with id {id} was not available in term {termId}"}, 404
	if term is None:
		average = course.getOverallRatingAverage(outof=outof, decimals=decimals)
	else:
		average = course.getRatingAverage(term, outof=outof, decimals=decimals)
	return {
		"average": average,
		"count": len(course.getRatings(term)),
		"distribution": course.getRatingsDistribution(term, outof, decimals)
	}, 200

@course.route("/<id>/grades", methods=["GET"])
@login_required
def getCourseGrades(id):
	course = Course.query.get(id)
	if not course:
		return {"error": f"Course with id {id} does not exist"}, 404
	termId = request.args.get("term", default=None, type=int)
	term = None
	if termId is not None:
		term = Term.query.get(termId)
		if not term:
			return {"error": f"Provided term id {termId} does not exist"}, 404
		if term not in course.calendar_terms:
			return {"error": f"Course with id {id} was not available in term {termId}"}, 404
	if term is None:
		average = course.getOverallGPVAverage()
	else:
		average = course.getGPVAverage(term)
	return {
		"average": average,
		"count": len(course.getGrades(term)),
		"distribution": course.getGradesDistribution(term)
	}, 200

@course.route("/code/<subjectCode>/<courseNumber>", methods=["GET"])
def getCourseByCode(subjectCode, courseNumber):
	subject = Subject.query.filter_by(code=subjectCode.upper()).first()
	if not subject:
		return {"error": f"Subject with code {subjectCode} does not exist"}, 404
	course = Course.query.filter_by(subject_id=subject.id, number=courseNumber).first()
	if not course:
		return {"error": f"Course with code {subjectCode}-{courseNumber} does not exist"}, 404
	return dict(course)
