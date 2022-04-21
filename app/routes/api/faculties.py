from app.models import Faculty
from app.routes.api.utils import *
from app.routes.api.subjects import getSubjects
from app.routes.api.courses import getCourses

from flask import Blueprint, request

faculty = Blueprint("faculties", __name__, url_prefix="/faculties")


#
# GET
#

@faculty.route("", methods=["GET"])
def getFaculties(name=""):
	# Parse name search query
	if not name:
		name = request.args.get("name", default="", type=str)
	name = name.strip().lower()
	
	# Filters tuple to check that the name query is included in the the selected faculties' name
	filters = (Faculty.name.ilike(f"%{name}%"),)
	
	return getAll(Faculty, filters)


@faculty.route("/<id>", methods=["GET"])
def getFacultyById(id):
	return getById(Faculty, id)


@faculty.route("/<id>/subjects", methods=["GET"])
def getFacultySubjects(id):
	if not Faculty.query.get(id):
		return {"error": f"Faculty with id {id} does not exist"}, 404
	return getSubjects(faculties=[int(id)])


@faculty.route("/<id>/courses", methods=["GET"])
def getFacultyCourses(id):
	if not Faculty.query.get(id):
		return {"error": f"Faculty with id {id} does not exist"}, 404
	return getCourses(faculties=[int(id)])
