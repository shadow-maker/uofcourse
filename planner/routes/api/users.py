# These routes are meant to be used internally by AJAX calls

# TODO: Add try statements to db.session.commit()

from planner import db
from planner.models import UserCourse, CourseCollection, Grade
from planner.queryUtils import *
from planner.constants import *

from planner.routes.api.utils import *

from flask import Blueprint, request
from flask_login import current_user

import json

user = Blueprint("users", __name__, url_prefix="/users")

#
# GET
#

# CourseCollection

@user.route("/collection/<id>/gpa")
def getCourseCollectionGpa(id):
	if not current_user.is_authenticated:
		return {"error": "User not logged in"}, 401

	collection = CourseCollection.query.filter_by(id=id).first()

	if not collection:
		return {"error": f"CourseCollection does not exist"}, 404

	if collection.user_id != current_user.id:
		return {"error": f"User (#{current_user.ucid}) does not have access to this CourseCollection"}, 403
	
	return {"gpa": collection.getGPA()}, 200

#
# POST
#

# User Course

@user.route("/course", methods=["POST"])
def postUserCourse(data={}):
	if not current_user.is_authenticated:
		return {"error": "User not logged in"}, 401

	if not data:
		data = request.form.to_dict()
		if not data:
			return {"error": "no data provided"}, 400
	if not "collection_id" in data:
		return {"error": "no CourseCollection id provided in data"}, 400
	if not "course_id" in data:
		return {"error": "no Course id provided in data"}, 400

	courseCollection = CourseCollection.query.filter_by(id=data["collection_id"]).first()
	if not courseCollection:
		return {"error": "CourseCollection not found"}, 404
	if courseCollection.user_id != current_user.id:
		return {"error": "User does not have access to this CourseCollection"}, 403
	
	course = Course.query.filter_by(id=data["course_id"]).first()
	if not course:
		return {"error": "Course not found"}, 404
	
	userCourse = UserCourse(courseCollection.id, course.id)

	db.session.add(userCourse)
	db.session.commit()
	
	return {"success": True}, 200

#
# PUT
#

# User Course

@user.route("/course", methods=["PUT"])
def putUserCourse(data={}):
	if not current_user.is_authenticated:
		return {"error": "User not logged in"}, 401

	if not data:
		data = request.form.to_dict()
		if not data:
			return {"error": "no data provided"}, 400
	if not "id" in data:
		return {"error": "no UserCourse id provided in data"}, 400

	userCourse = UserCourse.query.filter_by(id=data["id"]).first()

	if not userCourse:
		return {"error": "UserCourse not found"}, 404
	if not userCourse.ownedBy(current_user.id):
		return {"error": "User does not have access to this UserCourse"}, 403
	
	if "collection_id" in data:
		courseCollection = CourseCollection.query.filter_by(id=data["collection_id"]).first()
		if not courseCollection:
			return {"error": "CourseCollection not found"}, 404
		if courseCollection.user_id != current_user.id:
			return {"error": "User does not have access to this CourseCollection"}, 403
		userCourse.course_collection_id = courseCollection.id
	
	if "grade" in data:
		try:
			gradeId = json.loads(data["grade"])
		except:
			return {"error": "grade must be a float"}, 400
		if gradeId == 0:
			gradeId = None
		else:
			grade = Grade.query.filter_by(id=gradeId).first()
			if not grade:
				return {"error": "Grade not found"}, 404
		userCourse.grade_id = gradeId

	if "passed" in data:
		try:
			userCourse.passed = json.loads(data["passed"])
		except:
			return {"error": "passed must be a boolean"}, 400
	
	db.session.commit()
	
	return {"success": True}, 200


#
# DELETE
#

# CourseCollection

@user.route("/collection", defaults={"id":None}, methods=["DELETE"])
@user.route("/collection/<id>", methods=["DELETE"])
def delCourseCollection(data={}, id=None):
	if not current_user.is_authenticated:
		return {"error": "User not logged in"}, 401

	if not id:
		if not data:
			data = request.get_json()
		if not data:
			data = request.form.to_dict()
		if not data:
			return {"error": "no data provided"}, 400
		if not "id" in data:
			return {"error": "no CourseCollection id provided"}, 400
		id = data["id"]

	collection = CourseCollection.query.filter_by(id=id).first()

	if not collection:
		return {"error": f"CourseCollection does not exist"}, 404

	if collection.user_id != current_user.id:
		return {"error": f"User (#{current_user.ucid}) does not have access to this CourseCollection"}, 403
	
	if collection.userCourses:
		return {"error": f"CourseCollection is not empty"}, 400

	db.session.delete(collection)
	db.session.commit()

	return {"success": True}, 200


# UserCourse

@user.route("/course", defaults={"id":None}, methods=["DELETE"])
@user.route("/course/<id>", methods=["DELETE"])
def delUserCourse(data={}, id=None):
	if not current_user.is_authenticated:
		return {"error": "User not logged in"}, 401

	if not id:
		if not data:
			data = request.get_json()
		if not data:
			data = request.form.to_dict()
		if not data:
			return {"error": "no data provided"}, 400
		if not "id" in data:
			return {"error": "no UserCourse id provided"}, 400
		id = data["id"]

	userCourse = UserCourse.query.filter_by(id=id).first()

	if not userCourse:
		return {"error": f"UserCourse does not exist"}, 404

	if userCourse.collection.user_id != current_user.id:
		return {"error": f"User (#{current_user.ucid}) does not have access to this CourseCollection"}, 403

	db.session.delete(userCourse)
	db.session.commit()

	return {"success": True}, 200