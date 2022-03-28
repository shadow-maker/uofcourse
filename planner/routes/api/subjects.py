from planner.models import Subject
from planner import queryUtils as utils
from planner.routes.api.utils import *
from planner.routes.api.courses import getCoursesFilter

from flask import Blueprint, request

import json

subject = Blueprint("subjects", __name__, url_prefix="/subjects")


#
# GET
#

@subject.route("", methods=["GET"])
def getSubjects():
	return getAll(Subject, request.args)

@subject.route("/<id>", methods=["GET"])
def getSubjectById(id):
	return getById(Subject, id)

@subject.route("/<id>/courses", methods=["GET"])
def getSubjectCourses(id):
	if not utils.getById(Subject, id):
		return {"error": f"Subject with id {id} does not exist"}, 404
	return getCoursesFilter(data={
		"sort": request.args.get("sort", default=0, type=int),
		"asc": request.args.get("asc", default="true", type=str).lower(),
		"levels": json.loads(request.args.get("levels", default="[]", type=str)),
		"faculties": [],
		"subjects": [int(id)],
		"limit": request.args.get("limit", default=30, type=int),
		"page": request.args.get("page", default=1, type=int)
	})

@subject.route("/code/<code>", methods=["GET"])
def getSubjectByCode(code):
	subject = utils.getSubjectByCode(code)
	if not subject:
		return {"error": f"Subject with code {code} does not exist"}, 404
	return dict(subject), 200
