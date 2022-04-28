from app.models import db
from app.models import Subject, Faculty
from app.models import utils as utils
from app.routes.api.utils import *
from app.routes.api.courses import getCourses

from flask import Blueprint, request

subject = Blueprint("subjects", __name__, url_prefix="/subjects")


#
# GET
#


@subject.route("", methods=["GET"])
def getSubjects(name="", faculties=[]):
	# Parse name search query
	if not name:
		name = request.args.get("name", default="", type=str)
	name = name.strip().lower()

	# Parse faculties
	try:
		if not faculties: # faculties not passed as function argument
			faculties = request.args.getlist("faculty", type=int)
		if not faculties: # faculties not passed as url argument
			faculties = [f[0] for f in list(db.session.query(Faculty).with_entities(Faculty.id))]
		else: # check if faculties are valid
			for f in faculties:
				if not Faculty.query.get(f):
					return {"error": f"Invalid faculty {f}"}, 400
	except:
		return {"error": "Could not parse faculties, invalid format"}, 400
	
	# Filters tuple to check that the subject is in the selected faculties and name query is included in their name
	filters = (
		Subject.faculty_id.in_(faculties),
		Subject.name.ilike(f"%{name}%")
	)
	
	# Get results
	return getAll(Subject, filters)


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
	subject = utils.getSubjectByCode(code)
	if not subject:
		return {"error": f"Subject with code {code} does not exist"}, 404
	return dict(subject), 200
