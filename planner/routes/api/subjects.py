from planner.models import db
from planner.models import Subject, Faculty
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
	return getAll(Subject)


@subject.route("/<id>", methods=["GET"])
def getSubjectById(id):
	return getById(Subject, id)


@subject.route("/<id>/courses", methods=["GET"])
def getSubjectCourses(id):
	if not utils.getById(Subject, id):
		return {"error": f"Subject with id {id} does not exist"}, 404
	return getCoursesFilter(data={
		"levels": json.loads(request.args.get("levels", default="[]", type=str)),
		"faculties": [],
		"subjects": [int(id)]
	})


@subject.route("/code/<code>", methods=["GET"])
def getSubjectByCode(code):
	subject = utils.getSubjectByCode(code)
	if not subject:
		return {"error": f"Subject with code {code} does not exist"}, 404
	return dict(subject), 200


@subject.route("/filter", methods=["GET"])
def getSubjectsFilter(faculties=[]):
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
	
	filters = (Subject.faculty_id.in_(faculties))
	
	return getAll(Course, filters)
