from app import db
from app.models import Grade, Subject, Course, Collection, CollectionCourse
from app.auth import current_user

from flask import Blueprint, request

import json

me_course = Blueprint("course", __name__, url_prefix="/courses")

#
# GET
#

@me_course.route("/course/<id>", methods=["GET"])
def getCourseCollectionCourses(id):
	course = Course.query.get(id)
	if not course:
		return {"error": f"Course with id {id} does not exist"}, 404
	return {
		"results": [
			dict(cc) for cc in sorted(
				course.getCollectionCourses(current_user.id), key=lambda cc: cc.collection.term_id or 0
			)
		],
	}, 200

#
# POST
#

@me_course.route("/check", methods=["POST"])
def postCollectionCourseCheck(data={}):
	if not data:
		data = request.json
		if not data:
			return {"error": "no data provided"}, 400
	if not "collection_id" in data:
		return {"error": "no Collection id provided in data"}, 400

	collection = Collection.query.filter_by(id=data["collection_id"], user_id=current_user.id).first()
	if not collection:
		return {"error": "Collection from this user does not exist"}, 404

	if "course_id" in data:
		course = Course.query.get(data["course_id"])
	else:
		if not ("subject_code" in data or "course_number" in data):
			return {"error": "No course provided"}, 400
		subject = Subject.query.filter_by(code=data["subject_code"]).first()
		if not subject:
			return {"error": "Subject does not exist"}, 200
		course = Course.query.filter_by(subject_id=subject.id, number=data["course_number"]).first()
	if not course:
		return {"error": "Course does not exist"}, 200

	for cc in collection.collectionCourses:
		if cc.course_id == course.id:
			return {"error": "Course already in this term"}, 200

	if collection.term_id and collection.term not in course.calendar_terms:
		return {
			"warning": "Course was not available in this term's calendar",
			"course_id": course.id
		}, 200
	
	return {
		"success": "Course can be added to this term",
		"course_id": course.id
	}, 200

@me_course.route("", methods=["POST"])
def postCollectionCourse(data={}):
	response = {"success": True, "warnings": []}

	if not data:
		data = request.json
		if not data:
			return {"error": "no data provided"}, 400
	if not "collection_id" in data:
		return {"error": "no Collection id provided in data"}, 400
	if not "course_id" in data:
		return {"error": "no Course id provided in data"}, 400

	collection = Collection.query.filter_by(id=data["collection_id"], user_id=current_user.id).first()
	if not collection:
		return {"error": "Collection from this user does not exist"}, 404
	
	course = Course.query.get(data["course_id"])
	if not course:
		return {"error": "Course not found"}, 404
	for cc in collection.collectionCourses:
		if course.id == cc.course_id:
			return {"error": "a CollectionCourse with the same Course already exists in this Collection"}, 400
		
	if collection.term_id and collection.term not in collectionCourse.course.calendar_terms:
		response["warnings"].append("Course was not available in this term's calendar")
		response["not-available"] = True
	
	collectionCourse = CollectionCourse(collection.id, course.id)

	if collection.transfer:
		collectionCourse.grade = Grade.query.filter_by(symbol="CR").first()

	db.session.add(collectionCourse)
	db.session.commit()

	return response, 200

#
# PUT
#

@me_course.route("", defaults={"id":None}, methods=["PUT"])
@me_course.route("/<id>", methods=["PUT"])
def putCollectionCourse(data={}, id=None):
	response = {"success": True, "warnings": []}

	if not data:
		data = request.json
		if not data:
			return {"error": "no data provided"}, 400
	if not id:
		if not "id" in data:
			return {"error": "no CollectionCourse id provided"}, 400
		id = data["id"]

	collectionCourse = CollectionCourse.query.get(id)

	if not collectionCourse:
		return {"error": "CollectionCourse not found"}, 404
	if not collectionCourse.collection.user_id == current_user.id:
		return {"error": "User does not have access to this CollectionCourse"}, 403
	
	if "collection_id" in data:
		collection = Collection.query.filter_by(id=data["collection_id"], user_id=current_user.id).first()
		if not collection:
			return {"error": "Collection from this user does not exist"}, 404
		for cc in collection.collectionCourses:
			if collectionCourse != cc and collectionCourse.course_id == cc.course_id:
				return {"error": "a CollectionCourse with the same Course already exists in this Collection"}, 400
		collectionCourse.collection_id = collection.id

	if collection.term_id and collection.term not in collectionCourse.course.calendar_terms:
		response["warnings"].append("Course was not available in this term's calendar")
		response["not-available"] = True
	
	if "grade_id" in data:
		try:
			gradeId = json.loads(data["grade_id"])
		except:
			return {"error": "grade must be an int"}, 400
		if gradeId == 0:
			gradeId = None
		else:
			grade = Grade.query.get(gradeId)
			if not grade:
				return {"error": "Grade not found"}, 404
		collectionCourse.grade_id = gradeId

	if "passed" in data:
		try:
			collectionCourse.passed = data["passed"]
		except:
			return {"error": "passed must be a boolean"}, 400
	
	try:
		db.session.commit()
	except:
		return {"error": "error updating CollectionCourse"}, 500
	
	return response, 200

#
# DELETE
#

@me_course.route("", defaults={"id":None}, methods=["DELETE"])
@me_course.route("/<id>", methods=["DELETE"])
def delCollectionCourse(data={}, id=None):
	if not id:
		if not data:
			data = request.json
		if not data:
			return {"error": "no data provided"}, 400
		if not "id" in data:
			return {"error": "no CollectionCourse id provided"}, 400
		id = data["id"]

	collectionCourse = CollectionCourse.query.get(id)

	if not collectionCourse:
		return {"error": f"CollectionCourse does not exist"}, 404

	if collectionCourse.collection.user_id != current_user.id:
		return {"error": f"User does not have access to this CollectionCourse"}, 403

	try:
		db.session.delete(collectionCourse)
		db.session.commit()
	except:
		return {"error": "error deleting CollectionCourse"}, 500

	return {"success": True}, 200
