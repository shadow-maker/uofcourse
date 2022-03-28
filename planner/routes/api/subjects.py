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


@subject.route("/filter", methods=["GET"])
def getSubjectsFilter(data={}):
	allFaculties = [f[0] for f in list(db.session.query(Faculty).values(Faculty.id))]

	if not data:
		data = {
			"sort": request.args.get("sort", default=0, type=int),
			"asc": request.args.get("asc", default="true", type=str).lower(),
			"faculties": json.loads(request.args.get("faculties", default="[]", type=str)),
			"limit": request.args.get("limit", default=30, type=int),
			"page": request.args.get("page", default=1, type=int)
		}
	elif type(data) != dict:
		return {"error": f"Invalid data type ({type(data)} instead of dict)"}, 400

	try:
		if data["asc"] not in ["true", "1", "false", "0"]:
			return {"error": f"'{data['asc']}' is not a valid value for asc (boolean)"}, 400

		if data["sort"] not in range(len(SUBJECT_SORT_OPTIONS)):
			data["sort"] = 0
		sortBy = SUBJECT_SORT_OPTIONS[data["sort"]]

		if data["asc"] in ["false", "0"]:
			sortBy = [i.desc() for i in sortBy]
		
		faculties = [int(f) for f in data["faculties"] if int(f) in allFaculties]
		if not faculties:
			faculties = allFaculties

		limit = data["limit"]
		if limit > MAX_ITEMS_PER_PAGE:
			return {"error": f"limit of items per page cannot be greater than {MAX_ITEMS_PER_PAGE}"}, 400

		page = data["page"]

	except:
		return {"error": "could not parse data, invalid format"}, 400

	# Query database

	query = Subject.query.filter(
		Subject.faculty_id.in_(faculties)
	).order_by(*sortBy)

	results = query.paginate(per_page=limit, page=page)

	return {
		"results": [dict(s) for s in results.items],
		"page": page,
		"pages": results.pages,
		"total": results.total
	}, 200
