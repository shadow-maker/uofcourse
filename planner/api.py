from planner import app, db
from planner.models import Course, Subject, Faculty
from planner.queryUtils import *
from planner.constants import *

from flask import request, jsonify

import json

SORT_OPTIONS = [
	[Course.code, Course.name],
	[Course.name, Course.code]
]

@app.route("/api/c/filter", methods=["GET"])
def apiCoursesFilter():
	allLevels = COURSE_LEVELS
	allFaculties = [f[0] for f in list(db.session.query(Faculty).values(Faculty.id))]
	allSubjects = [s[0] for s in list(db.session.query(Subject).values(Subject.id))]

	# Get request data

	try:
		sortOpt = request.args.get("sort", default=0, type=int)
		if sortOpt not in range(len(SORT_OPTIONS)):
			sortOpt = 0
		sortBy = SORT_OPTIONS[sortOpt]

		if request.args.get("order", default="asc", type=str) != "asc":
			sortBy = [i.desc() for i in sortBy]

		levels = [l for l in json.loads(request.args.get("levels", default="[]", type=str)) if l in allLevels]
		if not levels:
			levels = allLevels
		
		faculties = [f for f in json.loads(request.args.get("faculties", default="[]", type=str)) if f in allFaculties]
		if not faculties:
			faculties = allFaculties

		temp = json.loads(request.args.get("subjects", default="[]", type=str))
		subjects = []
		for s in temp:
			if s in allSubjects:
				subjects.append(s)
			else:
				try:
					subjects.append(getSubjectByCode(s).id)
				except:
					pass
		if not subjects:
			subjects = allSubjects

		limit = request.args.get("limit", default=30, type=int)
		if limit > MAX_ITEMS_PER_PAGE:
			return jsonify({"error": f"limit of items per page cannot be greater than {MAX_ITEMS_PER_PAGE}"})

		page = request.args.get("page", default=1, type=int)

	except:
		return jsonify({"error": "could not parse data, invalid format"})

	# Query database

	query = Course.query.filter(
		Course.level.in_(levels),
		Course.subject_id.in_(
			[s for s in subjects if Subject.query.filter_by(id=s).first().faculty_id in faculties]
		)
	).order_by(*sortBy)

	results = query.paginate(per_page=limit, page=page)

	courses = [{
		"id": course.id,
		"name": course.name,
		"subj": course.subject.code,
		"code": course.code,
		"emoji": course.getEmoji(128218),
	} for course in results.items]

	return jsonify({
		"courses": courses,
		"page": page,
		"pages": results.pages,
		"total": results.total
	})
