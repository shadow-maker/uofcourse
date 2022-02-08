import collections
from flask_login import login_required, current_user
from planner import app, db
from planner.models import Course, Subject, Faculty, Term, User, CourseCollection
from planner.queryUtils import *
from planner.constants import *

from flask import request, jsonify

import json

SORT_OPTIONS = [
	[Course.code, Course.name],
	[Course.name, Course.code]
]

#
# GET
#

def apiById(table, id):
	object = getById(table, id)
	if not object:
		return jsonify({"error": f"{table.__name__} with id {id} does not exist"}), 404
	return jsonify(dict(object))


# Term

@app.route("/api/terms", methods=["GET"])
def apiTerms():
	return jsonify([dict(term) for term in Term.query.all()])

@app.route("/api/t/id/<id>", methods=["GET"])
def apiTermById(id):
	return apiById(Term, id)


# Faculty

@app.route("/api/f/id/<id>", methods=["GET"])
def apiFacultyById(id):
	return apiById(Faculty, id)


# Subject

@app.route("/api/s/id/<id>", methods=["GET"])
def apiSubjectById(id):
	return apiById(Subject, id)


@app.route("/api/s/code/<code>", methods=["GET"])
def apiSubjectByCode(code):
	subject = getSubjectByCode(code)
	if not subject:
		return jsonify({"error": f"Subject with code {code} does not exist"}), 404
	return jsonify(dict(subject))


# Course

@app.route("/api/c/id/<id>", methods=["GET"])
def apiCourseById(id):
	return apiById(Course, id)


@app.route("/api/c/code/<subjCode>/<courseCode>", methods=["GET"])
def apiCourseByCode(subjCode, courseCode):
	subject = getSubjectByCode(subjCode)
	if not subject:
		return jsonify({"error": f"Subject with code {subjCode} does not exist"}), 404
	course = Course.query.filter_by(subject_id=subject.id, code=courseCode).first()
	if not course:
		return jsonify({"error": f"Course with code {subjCode}-{courseCode} does not exist"}), 404
	return jsonify(dict(course))


def apiCoursesFilterHelper(data={}):
	allLevels = COURSE_LEVELS
	allFaculties = [f[0] for f in list(db.session.query(Faculty).values(Faculty.id))]
	allSubjects = [s[0] for s in list(db.session.query(Subject).values(Subject.id))]

	defaults = {
		"sort": 0,
		"order": "asc",
		"levels": [],
		"faculties": [],
		"subjects": [],
		"limit": 30,
		"page": 1
	}

	data = {k : data[k] if k in data and type(data[k]) == type(v) else v for k, v in defaults.items()}

	try:
		if data["sort"] not in range(len(SORT_OPTIONS)):
			data["sort"] = 0
		sortBy = SORT_OPTIONS[data["sort"]]

		if data["order"] != "asc":
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
					subjects.append(getSubjectByCode(s).id)
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

	query = Course.query.filter(
		Course.level.in_(levels),
		Course.subject_id.in_(
			[s for s in subjects if Subject.query.filter_by(id=s).first().faculty_id in faculties]
		)
	).order_by(*sortBy)

	results = query.paginate(per_page=limit, page=page)

	return {
		"courses": [{
			"id": course.id,
			"name": course.name,
			"subj": course.subject.code,
			"code": course.code,
			"emoji": course.getEmoji(),
		} for course in results.items],
		"page": page,
		"pages": results.pages,
		"total": results.total
	}


@app.route("/api/c/filter", methods=["GET"])
def apiCoursesFilter():
	return jsonify(apiCoursesFilterHelper({
		"sort": request.args.get("sort", default=0, type=int),
		"order": request.args.get("order", default="asc", type=str),
		"levels": json.loads(request.args.get("levels", default="[]", type=str)),
		"faculties": json.loads(request.args.get("faculties", default="[]", type=str)),
		"subjects": json.loads(request.args.get("subjects", default="[]", type=str)),
		"limit": request.args.get("limit", default=30, type=int),
		"page": request.args.get("page", default=1, type=int)
	}))



#
# POST
#

# CourseCollection

@app.route("/api/u/collection/<termId>", methods=["POST"])
def apiAddCourseCollection(termId):
	if not current_user.is_authenticated:
		return jsonify({"error": "User not logged in"}), 401

	if not Term.query.filter_by(term_id=termId).first():
		return jsonify({"error": f"Term {termId} does not exist"}), 404

	if CourseCollection.query.filter_by(user_id=current_user.id, term_id=termId):
		return jsonify({"error": f"User (#{current_user.id}) already has a collection for term {termId}"}), 400

	db.session.add(CourseCollection(user_id=current_user.id, term_id=termId))
	db.session.commit()
	return jsonify({"success": True})



#
# DELETE
#

# CourseCollection

@app.route("/api/u/collection/<id>", methods=["DELETE"])
def apiDelCourseCollection(id):
	if not current_user.is_authenticated:
		return jsonify({"error": "User not logged in"}), 401

	collection = CourseCollection.query.filter_by(id=id).first()

	if not collection:
		return jsonify({"error": f"CourseCollection {id} does not exist"}), 404

	if collection.user_id != current_user.id:
		return jsonify({"error": f"User (#{current_user.id}) does not have access to this CourseCollection"}), 403
	
	if collection.userCourses:
		return jsonify({"error": f"CourseCollection {id} is not empty"}), 400

	db.session.delete(collection)
	db.session.commit()
	return jsonify({"success": True})