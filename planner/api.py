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

@app.route("/api/c/filter", methods=["GET", "POST"])
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

	page = 1

	if request.method == "POST":
		if request.form:
			data = request.form
		elif request.json:
			data = request.json
		else:
			return jsonify({"error": "No data passed through json or form"})

		# Sort
		if "sortBy" in data:
			sortOpt = int(data["sortBy"]) if int(data["sortBy"]) in range(len(SORT_OPTIONS)) else 0
		sortBy = SORT_OPTIONS[sortOpt]
		
		if "orderBy" in data and data["orderBy"] != "asc":
			sortBy = [i.desc() for i in sortBy]

		# Filter

		if "selectedLevel" in data:
			selected = json.loads(data["selectedLevel"])
			for l in levels:
				levels[l] = l in selected
		
		if "selectedFaculty" in data:
			selected = json.loads(data["selectedFaculty"])
			for f in faculties:
				faculties[f]["sel"] = f in selected

		if "selectedSubject" in data:
			selected = json.loads(data["selectedSubject"])
			for s in subjects:
				subjects[s]["sel"] = s in selected

		if "page" in data:
			page = int(data["page"])

	levelIds = [l for l, sel in levels.items() if sel]

	facIds = [int(f) for f, v in faculties.items() if v["sel"]]

	subjIds = [s for s in subjects if subjects[s]["sel"]]
	if not subjIds:
		subjIds = [s[0] for s in list(db.session.query(Subject).values(Subject.id))]
	subjIds = [s for s in subjIds if Subject.query.filter_by(id=s).first().faculty_id in facIds]

	query = Course.query.filter(Course.level.in_(levelIds), Course.subject_id.in_(subjIds)).order_by(*sortBy)

	results = query.paginate(per_page=30, page=page)

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
