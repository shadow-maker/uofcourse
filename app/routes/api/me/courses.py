from app import db
from app.models import Grade, Course, Collection, CollectionCourse
from app.auth import current_user

from flask import Blueprint, request

import json

me_course = Blueprint("course", __name__, url_prefix="/courses")

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

# User Course

@me_course.route("", methods=["POST"])
def postCollectionCourse(data={}):
	if not data:
		data = request.form.to_dict()
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
	
	try:
		collectionCourse = CollectionCourse(collection.id, course.id)

		db.session.add(collectionCourse)
		db.session.commit()
	except:
		return {"error": "error creating CollectionCourse"}, 500
	
	return {"success": True}, 200

#
# PUT
#

@me_course.route("", defaults={"id":None}, methods=["PUT"])
@me_course.route("/<id>", methods=["PUT"])
def putCollectionCourse(data={}, id=None):
	if not data:
		data = request.form.to_dict()
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
			collectionCourse.passed = json.loads(data["passed"])
		except:
			return {"error": "passed must be a boolean"}, 400
	
	try:
		db.session.commit()
	except:
		return {"error": "error updating CollectionCourse"}, 500
	
	return {"success": True}, 200

#
# DELETE
#

@me_course.route("", defaults={"id":None}, methods=["DELETE"])
@me_course.route("/<id>", methods=["DELETE"])
def delCollectionCourse(data={}, id=None):
	if not id:
		if not data:
			data = request.form.to_dict()
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
