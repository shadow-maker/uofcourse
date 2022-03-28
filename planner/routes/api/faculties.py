from planner.models import Faculty, Subject
from planner import queryUtils as utils
from planner.routes.api.utils import *
from planner.routes.api.subjects import getSubjectsFilter
from planner.routes.api.courses import getCoursesFilter

from flask import Blueprint, request

import json

faculty = Blueprint("faculties", __name__, url_prefix="/faculties")


#
# GET
#

@faculty.route("", methods=["GET"])
def getFaculties():
	return getAll(Faculty, request.args)


@faculty.route("/<id>", methods=["GET"])
def getFacultyById(id):
	return getById(Faculty, id)


@faculty.route("/<id>/subjects", methods=["GET"])
def getFacultySubjects(id):
	if not utils.getById(Faculty, id):
		return {"error": f"Faculty with id {id} does not exist"}, 404
	return getSubjectsFilter(data={
		"sort": request.args.get("sort", default=0, type=int),
		"asc": request.args.get("asc", default="true", type=str).lower(),
		"faculties": [int(id)],
		"limit": request.args.get("limit", default=30, type=int),
		"page": request.args.get("page", default=1, type=int)
	})


@faculty.route("/<id>/courses", methods=["GET"])
def getFacultyCourses(id):
	if not utils.getById(Faculty, id):
		return {"error": f"Faculty with id {id} does not exist"}, 404
	return getCoursesFilter(data={
		"sort": request.args.get("sort", default=0, type=int),
		"asc": request.args.get("asc", default="true", type=str).lower(),
		"levels": json.loads(request.args.get("levels", default="[]", type=str)),
		"faculties": [int(id)],
		"subjects": json.loads(request.args.get("subjects", default="[]", type=str)),
		"limit": request.args.get("limit", default=30, type=int),
		"page": request.args.get("page", default=1, type=int)
	})
