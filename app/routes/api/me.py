# These routes are meant to be used internally by AJAX calls

from app import db
from app.models import Grade, Course, UserLog, UserCourse, CourseCollection
from app.auth import current_user, login_required
from app.constants import *
from app.routes.api.utils import *

from flask import Blueprint, request, session

import json

me = Blueprint("me", __name__, url_prefix="/me")

# Validate login for all /api/me routes

@me.before_request
@login_required
def before_request():
	pass

#
# GET
#

# UserLog

@me.route("/logs")
def getUserLogs():
	filters = (
		UserLog.user_id == current_user.id,
	)
	return getAll(UserLog, filters)


@me.route("/logs/<id>")
def getUserLog(id):
	log = UserLog.query.filter_by(id=id, user_id=current_user.id).first()
	if not log:
		return {"error": "log not found"}, 404
	return dict(log), 200


@me.route("/logs/<id>/location")
def getUserLogLocation(id):
	log = UserLog.query.filter_by(id=id, user_id=current_user.id).first()
	if not log:
		return {"error": "log not found"}, 404
	return log.location, 200


# CourseCollection

@me.route("/collections")
def getCourseCollections():
	sort = list(dict.fromkeys(request.args.getlist("sort", type=str)))
	asc = request.args.get("asc", default="true", type=str).lower()

	# Get list of table columns for sorting
	order = []
	for column in sort:
		try:
			col = getattr(CourseCollection, column)
			if not issubclass(type(col), QueryableAttribute):
				raise AttributeError
		except AttributeError:
			return {"error": f"'{column}' is not a valid column for CourseCollection"}, 400
		order.append(col)
	order.append(CourseCollection.id)

	# Add sorting columns to desc() if asc is false
	if asc in ["false", "0"]:
		order = [desc(i) for i in order]

	# Query database
	try:
		results = CourseCollection.query.filter_by(user_id=current_user.id).order_by(*order).all()
	except:
		return {"error": "sort columns are not valid"}, 400
		
	return {"collections": [dict(collection) for collection in results]}, 200

@me.route("/collections/<id>")
def getCourseCollection(id):
	collection = CourseCollection.query.filter_by(id=id).first()

	if not collection:
		return {"error": f"CourseCollection does not exist"}, 404

	if collection.user_id != current_user.id:
		return {"error": f"User (#{current_user.id}) does not have access to this CourseCollection"}, 403
	
	return dict(collection), 200

@me.route("/collections/<id>/courses")
def getCourseCollectionCourses(id):
	collection = CourseCollection.query.filter_by(id=id).first()

	if not collection:
		return {"error": f"CourseCollection does not exist"}, 404

	if collection.user_id != current_user.id:
		return {"error": f"User (#{current_user.id}) does not have access to this CourseCollection"}, 403
	
	return {"courses": [dict(course) for course in collection.userCourses]}, 200

@me.route("/collections/<id>/gpa")
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

@me.route("/course", methods=["POST"])
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

@me.route("/session/welcome", methods=["PUT"])
def putSessionWelcome():
	data = request.form.to_dict()
	if not "set" in data:
		if "welcome" in session and session["welcome"] == False:
			session["welcome"] = True
		else:
			session["welcome"] = False
	else:
		try:
			session["welcome"] = bool(json.loads(data["set"]))
		except:
			return {"error": "invalid 'set' value in data"}, 400
	return {"success": True}, 200

@me.route("/session/transferred", methods=["PUT"])
def putSessionTransferred():
	data = request.form.to_dict()
	if not "set" in data:
		if "transferred" in session and session["transferred"] == False:
			session["transferred"] = True
		else:
			session["transferred"] = False
	else:
		try:
			session["transferred"] = bool(json.loads(data["set"]))
		except:
			return {"error": "invalid 'set' value in data"}, 400
	return {"success": True}, 200

# User Course

@me.route("/course", methods=["PUT"])
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
	
	try:
		db.session.commit()
	except:
		return {"error": "error updating UserCourse"}, 500
	
	return {"success": True}, 200


#
# DELETE
#

# CourseCollection

# @me.route("/collection", defaults={"id":None}, methods=["DELETE"])
# @me.route("/collection/<id>", methods=["DELETE"])
# def delCourseCollection(data={}, id=None):
# 	if not id:
# 		if not data:
# 			data = request.get_json()
# 		if not data:
# 			data = request.form.to_dict()
# 		if not data:
# 			return {"error": "no data provided"}, 400
# 		if not "id" in data:
# 			return {"error": "no CourseCollection id provided"}, 400
# 		id = data["id"]

# 	collection = CourseCollection.query.filter_by(id=id).first()

# 	if not collection:
# 		return {"error": f"CourseCollection does not exist"}, 404

# 	if collection.user_id != current_user.id:
# 		return {"error": f"User (#{current_user.id}) does not have access to this CourseCollection"}, 403
	
# 	if collection.userCourses:
# 		return {"error": f"CourseCollection is not empty"}, 400

# 	db.session.delete(collection)
# 	db.session.commit()

# 	return {"success": True}, 200


# UserCourse

@me.route("/course", defaults={"id":None}, methods=["DELETE"])
@me.route("/course/<id>", methods=["DELETE"])
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

	try:
		db.session.delete(userCourse)
		db.session.commit()
	except:
		return {"error": "error deleting UserCourse"}, 500

	return {"success": True}, 200
