from app.models import Subject, Faculty
from app.routes.api.utils import *
from app.routes.api.courses import getCourses

from flask import Blueprint, request

subject = Blueprint("subjects", __name__, url_prefix="/subjects")


#
# GET
#


@subject.route("", methods=["GET"])
def getSubjects(name="", faculties=[], old=None):
	# Parse name search query
	try:
		if not name:
			name = request.args.get("name", default="", type=str)
		name = name.strip().lower()
	except:
		return {"error": "Could not parse name, invalid format"}, 400

	# Parse faculties
	try:
		if not faculties: # faculties not passed as function argument
			faculties = list(dict.fromkeys(request.args.getlist("faculty", type=int)))
		for f in faculties: # check if faculties are valid
			if not Faculty.query.get(f):
				return {"error": f"Invalid faculty {f}"}, 400
	except:
		return {"error": "Could not parse faculties, invalid format"}, 400

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
		Subject.name.ilike(f"%{name}%")
	]
	if faculties:
		filters.append(Subject.faculty_id.in_(faculties))
	if old is not None:
		filters.append(Subject.old == old)
	
	# Get results
	return getAll(Subject, tuple(filters))


@subject.route("/<id>", methods=["GET"])
def getSubjectById(id):
	return getById(Subject, id)


@subject.route("/<id>/courses", methods=["GET"])
def getSubjectCourses(id):
	if not Subject.query.get(id):
		return {"error": f"Subject with id {id} does not exist"}, 404
	return getCourses(subjects=[int(id)])


@subject.route("/code/<code>", methods=["GET"])
def getSubjectByCode(code):
	subject = Subject.query.filter_by(code=code.upper()).first()
	if not subject:
		return {"error": f"Subject with code {code} does not exist"}, 404
	return dict(subject), 200
