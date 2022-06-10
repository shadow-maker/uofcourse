from app import db
from app.models import Grade, Course, CourseCollection, UserCourse
from app.auth import current_user

from flask import Blueprint, request

import json

me_course = Blueprint("course", __name__, url_prefix="/courses")

@me_course.route("/course/<id>", methods=["GET"])
def getCourseUserCourses(id):
	course = Course.query.get(id)
	if not course:
		return {"error": f"Course with id {id} does not exist"}, 404
	return {"collection_courses": [dict(uc) for uc in course.getUserCourses(current_user.id)]}, 200

#
# POST
#

# User Course

@me_course.route("", methods=["POST"])
def postUserCourse(data={}):
	if not data:
		data = request.form.to_dict()
		if not data:
			return {"error": "no data provided"}, 400
	if not "collection_id" in data:
		return {"error": "no CourseCollection id provided in data"}, 400
	if not "course_id" in data:
		return {"error": "no Course id provided in data"}, 400

	collection = CourseCollection.query.filter_by(id=data["collection_id"], user_id=current_user.id).first()
	if not collection:
		return {"error": "CourseCollection from this user does not exist"}, 404
	
	course = Course.query.get(data["course_id"])
	if not course:
		return {"error": "Course not found"}, 404
	for userCourse in collection.userCourses:
		if course.id == userCourse.course_id:
			return {"error": "a UserCourse with the same Course already exists in this CourseCollection"}, 400
	
	try:
		userCourse = UserCourse(collection.id, course.id)

		db.session.add(userCourse)
		db.session.commit()
	except:
		return {"error": "error creating UserCourse"}, 500
	
	return {"success": True}, 200

#
# PUT
#

@me_course.route("", defaults={"id":None}, methods=["PUT"])
@me_course.route("/<id>", methods=["PUT"])
def putUserCourse(data={}, id=None):
	if not data:
		data = request.form.to_dict()
		if not data:
			return {"error": "no data provided"}, 400
	if not id:
		if not "id" in data:
			return {"error": "no UserCourse id provided"}, 400
		id = data["id"]

	userCourse = UserCourse.query.get(id)

	if not userCourse:
		return {"error": "UserCourse not found"}, 404
	if not userCourse.collection.user_id == current_user.id:
		return {"error": "User does not have access to this UserCourse"}, 403
	
	if "collection_id" in data:
		collection = CourseCollection.query.filter_by(id=data["collection_id"], user_id=current_user.id).first()
		if not collection:
			return {"error": "CourseCollection from this user does not exist"}, 404
		for uCourse in collection.userCourses:
			if userCourse != uCourse and userCourse.course_id == uCourse.course_id:
				return {"error": "a UserCourse with the same Course already exists in this CourseCollection"}, 400
		userCourse.course_collection_id = collection.id
	
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
		userCourse.grade_id = gradeId

	if "passed" in data:
		try:
			userCourse.passed = json.loads(data["passed"])
		except:
			return {"error": "passed must be a boolean"}, 400
	
	try:
		db.session.commit()
	except:
		return {"error": "error updating UserCourse"}, 500
	
	return {"success": True}, 200

#
# DELETE
#

@me_course.route("", defaults={"id":None}, methods=["DELETE"])
@me_course.route("/<id>", methods=["DELETE"])
def delUserCourse(data={}, id=None):
	if not id:
		if not data:
			data = request.form.to_dict()
		if not data:
			return {"error": "no data provided"}, 400
		if not "id" in data:
			return {"error": "no UserCourse id provided"}, 400
		id = data["id"]

	userCourse = UserCourse.query.get(id)

	if not userCourse:
		return {"error": f"UserCourse does not exist"}, 404

	if userCourse.collection.user_id != current_user.id:
		return {"error": f"User does not have access to this UserCourse"}, 403

	try:
		db.session.delete(userCourse)
		db.session.commit()
	except:
		return {"error": "error deleting UserCourse"}, 500

	return {"success": True}, 200
