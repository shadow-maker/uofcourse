# These routes are meant to be used internally by AJAX calls

# TODO: Add try statements to db.session.commit()

from app import db
from app.models import Grade, Course, UserLog, UserCourse, CourseCollection
from app.auth import current_user, login_required
from app.constants import *
from app.routes.api.utils import *

from flask import Blueprint, request, session

import json

user = Blueprint("users", __name__, url_prefix="/users")

#
# GET
#

# UserLog

@user.route("/logs")
@login_required
def getUserLogs():
	filters = (
		UserLog.user_id == current_user.id,
	)
	return getAll(UserLog, filters)


@user.route("/logs/<id>")
@login_required
def getUserLog(id):
	log = UserLog.query.filter_by(id=id, user_id=current_user.id).first()
	if not log:
		return {"error": "log not found"}, 404
	return dict(log), 200


@user.route("/logs/<id>/location")
@login_required
def getUserLogLocation(id):
	log = UserLog.query.filter_by(id=id, user_id=current_user.id).first()
	if not log:
		return {"error": "log not found"}, 404
	return log.location, 200


# CourseCollection

@user.route("/collection/<id>/gpa")
@login_required
def getCourseCollectionGpa(id, precision=3):
	collection = CourseCollection.query.filter_by(id=id).first()

	if not collection:
		return {"error": f"CourseCollection does not exist"}, 404

	if collection.user_id != current_user.id:
		return {"error": f"User (#{current_user.id}) does not have access to this CourseCollection"}, 403
	
	return {
		"points": collection.getPoints(precision),
		"units": collection.units,
		"gpa": collection.getGPA(precision)
	}, 200

#
# POST
#

# User Course

@user.route("/course", methods=["POST"])
@login_required
def postUserCourse(data={}):
	if not data:
		data = request.form.to_dict()
		if not data:
			return {"error": "no data provided"}, 400
	if not "collection_id" in data:
		return {"error": "no CourseCollection id provided in data"}, 400
	if not "course_id" in data:
		return {"error": "no Course id provided in data"}, 400

	collection = CourseCollection.query.filter_by(id=data["collection_id"]).first()
	if not collection:
		return {"error": "CourseCollection not found"}, 404
	if collection.user_id != current_user.id:
		return {"error": "User does not have access to this CourseCollection"}, 403
	
	course = Course.query.filter_by(id=data["course_id"]).first()
	if not course:
		return {"error": "Course not found"}, 404
	for userCourse in collection.userCourses:
		if course.id == userCourse.course_id:
			return {"error": "a UserCourse with the same Course already exists in this CourseCollection"}, 400
	
	userCourse = UserCourse(collection.id, course.id)

	db.session.add(userCourse)
	db.session.commit()
	
	return {"success": True}, 200

#
# PUT
#

@user.route("/session/welcome", methods=["PUT"])
@login_required
def putSessionWelcome():
	data = request.form.to_dict()
	if not "set" in data:
		if "welcome" in session and session["welcome"] == False:
			session["welcome"] = True
		else:
			session["welcome"] = False
	else:
		session["welcome"] = bool(json.loads(data["set"]))
	return {"success": True}, 200

@user.route("/session/transferred", methods=["PUT"])
@login_required
def putSessionTransferred():
	data = request.form.to_dict()
	if not "set" in data:
		if "transferred" in session and session["transferred"] == False:
			session["transferred"] = True
		else:
			session["transferred"] = False
	else:
		session["transferred"] = bool(json.loads(data["set"]))
	return {"success": True}, 200

# User Course

@user.route("/course", methods=["PUT"])
@login_required
def putUserCourse(data={}):
	if not data:
		data = request.form.to_dict()
		if not data:
			return {"error": "no data provided"}, 400
	if not "id" in data:
		return {"error": "no UserCourse id provided in data"}, 400

	userCourse = UserCourse.query.filter_by(id=data["id"]).first()

	if not userCourse:
		return {"error": "UserCourse not found"}, 404
	if not userCourse.collection.user_id == current_user.id:
		return {"error": "User does not have access to this UserCourse"}, 403
	
	if "collection_id" in data:
		collection = CourseCollection.query.filter_by(id=data["collection_id"]).first()
		if not collection:
			return {"error": "CourseCollection not found"}, 404
		if collection.user_id != current_user.id:
			return {"error": "User does not have access to this CourseCollection"}, 403
		for uCourse in collection.userCourses:
			if userCourse != uCourse and userCourse.course_id == uCourse.course_id:
				return {"error": "a UserCourse with the same Course already exists in this CourseCollection"}, 400
		userCourse.course_collection_id = collection.id
	
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
@login_required
def delCourseCollection(data={}, id=None):
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
		return {"error": f"User (#{current_user.id}) does not have access to this CourseCollection"}, 403
	
	if collection.userCourses:
		return {"error": f"CourseCollection is not empty"}, 400

	db.session.delete(collection)
	db.session.commit()

	return {"success": True}, 200


# UserCourse

@user.route("/course", defaults={"id":None}, methods=["DELETE"])
@user.route("/course/<id>", methods=["DELETE"])
@login_required
def delUserCourse(data={}, id=None):
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
		return {"error": f"User (#{current_user.id}) does not have access to this CourseCollection"}, 403

	db.session.delete(userCourse)
	db.session.commit()

	return {"success": True}, 200
