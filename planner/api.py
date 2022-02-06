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

def parseData(data): # data is dict or ImmutableMultiDict
	parsed = {}
	for key, value in data.items():
		try:
			parsed[key] = json.loads(value)
		except:
			parsed[key] = value
	return parsed


@app.route("/api/c/filter", methods=["GET"])
def coursesFilter():
	sortOpt = 0
	sortBy = SORT_OPTIONS[sortOpt]

	levels = {l : True for l in COURSE_LEVELS}
	faculties = {
		f[0] : {"name": f[1], "sel": True}
	for f in list(db.session.query(Faculty).values(Faculty.id, Faculty.name))}
	subjects = {
		s[0] : {"code": s[1], "sel": False}
	for s in list(db.session.query(Subject).values(Subject.id, Subject.code))}

	limit = 30
	page = 1

	data = request.args.to_dict()
	if data:
		try:
			data = parseData(data)
		except:
			return jsonify({"error": "Data couldn't be parsed, is in incorrect format"})

		# Sort
		if "sort" in data:
			sortOpt = int(data["sort"])
			if sortOpt not in range(len(SORT_OPTIONS)):
				sortOpt = 0
		sortBy = SORT_OPTIONS[sortOpt]
		
		if "order" in data and data["order"] != "asc":
			sortBy = [i.desc() for i in sortBy]

		# Filter

		if "levels" in data:
			levels = {l : l in data["levels"] for l in levels}
		
		if "faculties" in data:
			for f in faculties:
				faculties[f]["sel"] = f in data["faculties"]

		if "subjects" in data:
			selected = []
			for s in data["subjects"]:
				if type(s) == int:
					selected.append(s)
				else:
					try:
						selected.append(getSubjectByCode(s).id)
					except:
						pass
			for s in subjects:
				subjects[s]["sel"] = s in selected

		if "limit" in data:
			limit = int(data["limit"])
			if limit > MAX_ITEMS_PER_PAGE:
				return jsonify({"error": f"limit of items per page cannot be greater that {MAX_ITEMS_PER_PAGE}"})

		if "page" in data:
			page = int(data["page"])

	levelIds = [l for l, sel in levels.items() if sel]

	facIds = [int(f) for f, v in faculties.items() if v["sel"]]

	subjIds = [s for s in subjects if subjects[s]["sel"]]
	if not subjIds:
		subjIds = [s[0] for s in list(db.session.query(Subject).values(Subject.id))]
	subjIds = [s for s in subjIds if Subject.query.filter_by(id=s).first().faculty_id in facIds]

	query = Course.query.filter(Course.level.in_(levelIds), Course.subject_id.in_(subjIds)).order_by(*sortBy)

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
