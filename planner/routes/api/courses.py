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
	return getAll(Course, request.args)


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
def getCoursesFilter():
	allLevels = COURSE_LEVELS
	allFaculties = [f[0] for f in list(db.session.query(Faculty).values(Faculty.id))]
	allSubjects = [s[0] for s in list(db.session.query(Subject).values(Subject.id))]

	try:
		data ={
			"sort": request.args.get("sort", default=0, type=int),
			"asc": request.args.get("asc", default="true", type=str).lower(),
			"levels": json.loads(request.args.get("levels", default="[]", type=str)),
			"faculties": json.loads(request.args.get("faculties", default="[]", type=str)),
			"subjects": json.loads(request.args.get("subjects", default="[]", type=str)),
			"limit": request.args.get("limit", default=30, type=int),
			"page": request.args.get("page", default=1, type=int)
		}

		if data["asc"] not in ["true", "1", "false", "0"]:
			return {"error": f"'{data['asc']}' is not a valid value for asc (boolean)"}, 400


		if data["sort"] not in range(len(SORT_OPTIONS)):
			data["sort"] = 0
		sortBy = SORT_OPTIONS[data["sort"]]

		if data["asc"] in ["false", "0"]:
			sortBy = [i.desc() for i in sortBy]

		levels = [l for l in data["levels"] if l in allLevels]
		if not levels:
			levels = allLevels
		
		faculties = [f for f in data["faculties"] if f in allFaculties]
		if not faculties:
			faculties = allFaculties

		subjects = []
		for s in data["subjects"]:
			if s in allSubjects:
				subjects.append(s)
			else:
				try:
					subjects.append(utils.getSubjectByCode(s).id)
				except:
					pass
		if not subjects:
			subjects = allSubjects

		limit = data["limit"]
		if limit > MAX_ITEMS_PER_PAGE:
			return {"error": f"limit of items per page cannot be greater than {MAX_ITEMS_PER_PAGE}"}, 400

		page = data["page"]

	except:
		return {"error": "could not parse data, invalid format"}, 400

	# Query database

	queryLevels = []
	for l in levels:
		if queryLevels and queryLevels[-1][1] == l:
			queryLevels[-1][1] = l + 1
		else:
			queryLevels.append([l, l + 1])

	query = Course.query.filter(
		or_(and_(Course.code >= l[0] * 100, Course.code < l[1] * 100) for l in queryLevels),
		Course.subject_id.in_(
			[s for s in subjects if Subject.query.filter_by(id=s).first().faculty_id in faculties]
		)
	).order_by(*sortBy)

	results = query.paginate(per_page=limit, page=page)

	return {
		"results": [{
			"id": c.id,
			"name": c.name,
			"subject_id": c.subject_id,
			"code": c.code,
			"code_full": c.code_full,
			"emoji": c.getEmoji(),
			"url": c.url,
			"tags": [tag.id for tag in c.userTags if tag.user_id == current_user.id] if current_user.is_authenticated else [],
			"collections": [dict(uc.collection) for uc in c.getUserCourses(current_user.id)] if current_user.is_authenticated else []
		} for c in results.items],
		"page": page,
		"pages": results.pages,
		"total": results.total
	}, 200