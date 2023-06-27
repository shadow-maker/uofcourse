from app import db
from app.models import Grade, Subject, Course, CustomCourse, Collection, CollectionCourse
from app.auth import current_user

from flask import Blueprint, request

import json

me_course = Blueprint("course", __name__, url_prefix="/courses")

#
# GET
#

@me_course.route("/<id>", methods=["GET"])
def getCollectionCourse(id):
	cc = CollectionCourse.query.get(id)
	if not cc:
		return {"error": f"CollectionCourse with id {id} does not exist"}, 404
	if cc.user_id != current_user.id:
		return {"error": "CollectionCourse does not belong to this user"}, 403
	return dict(cc), 200

@me_course.route("/<id>/course", methods=["GET"])
def getCollectionCourseCourse(id):
	cc = CollectionCourse.query.get(id)
	if not cc:
		return {"error": f"CollectionCourse with id {id} does not exist"}, 404
	if cc.user_id != current_user.id:
		return {"error": "CollectionCourse does not belong to this user"}, 403
	course = cc.course
	if course is None:
		return {"error": f"Course of CollectionCourse {cc.id} does not exist"}, 404
	return dict(course), 200

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

	code = data["subject_code"] + "-" + data["course_number"]
	for cc in collection.collectionCourses:
		if cc.course.code == code:
			return {"error": "Course already in this term"}, 200

	if not course:
		return {
			"warnings": ["Course does not exist"],
			"course_id": None
		}, 200

	for cc in collection.collectionCourses:
		if cc.course_id == course.id:
			return {"error": "Course already in this term"}, 200

	warnings = []
	if collection.term_id and collection.term not in course.calendar_terms:
		warnings.append("Course was not available in this term's calendar")
	if not course.repeat:
		for col in current_user.collections:
			if col.id == collection.id:
				continue
			for cc in col.collectionCourses:
				if (cc.grade is not None or col.term.isPrev()) and course.id == cc.course_id:
					warnings.append(
						f"Course already Transferred and cannot be repeated"
						if col.transfer else
						f"Course already taken in {col.term.name} and cannot be repeated"
					)
					break
	
	if len(warnings) > 0:
		return {
			"warnings": warnings,
			"course_id": course.id
		}, 200
	else:
		return {
			"success": "Course can be added to this term",
			"course_id": course.id
		}, 200

@me_course.route("", methods=["POST"])
def postCollectionCourse(data={}):
	custom = False
	collectionCourse = None
	response = {"success": True, "warnings": []}

	if not data:
		data = request.json
		if not data:
			return {"error": "no data provided"}, 400
	if not "collection_id" in data:
		return {"error": "no Collection id provided in data"}, 400
	collection = Collection.query.filter_by(id=data["collection_id"], user_id=current_user.id).first()
	if not collection:
		return {"error": "Collection from this user does not exist"}, 404

	if "custom" in data:
		custom = bool(data["custom"])
	if custom:
		if not "subject_code" in data:
			return {"error": "no Subject code provided in data"}, 400
		if not "number" in data:
			return {"error": "no Course number provided in data"}, 400
		
		course = CustomCourse(data["subject_code"], data["number"])

		if "name" in data:
			course.name = data["name"]
		if "units" in data:
			course.units = float(data["units"])
		if "repeat" in data:
			course.repeat = bool(data["repeat"])
		if "countgpa" in data:
			course.countgpa = bool(data["countgpa"])

		try:
			db.session.add(course)
			db.session.commit()
		except:
			db.session.rollback()
			return {"error": "error creating Custom Course"}, 500
		
		collectionCourse = CollectionCourse(collection.id, custom_course_id=course.id)
		
	else:
		if not "course_id" in data:
			return {"error": "no Course id provided in data"}, 400

		course = Course.query.get(data["course_id"])
		if not course:
			return {"error": "Course not found"}, 404
		for cc in collection.collectionCourses:
			if course.id == cc.course_id:
				return {"error": "a CollectionCourse with the same Course already exists in this Collection"}, 400
		if not collection.isCalendarAvailable(course):
			response["warnings"].append(f"Course {course.code} was not available in this term's calendar")
			response["not-available"] = True
		if not course.repeat:
			for col in current_user.collections:
				if col.id == collection.id:
					continue
				for cc in col.collectionCourses:
					if course.id == cc.course_id:
						response["warnings"].append(
							f"Course {course.code} already Transferred and cannot be repeated"
							if col.transfer else
							f"Course {course.code} already taken in term {col.term.name} and cannot be repeated"
							)
						response["taken"] = True
						break
	
		collectionCourse = CollectionCourse(collection.id, course_id=course.id)

	if collection.transfer:
		collectionCourse.grade = Grade.query.filter_by(symbol="CR").first()

	try:
		db.session.add(collectionCourse)
		db.session.commit()
	except:
		db.session.rollback()
		return {"error": "error creating Collection Course"}, 500

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
		if (collection.transfer or not collection.isTaken()) and collectionCourse.rating is not None:
			db.session.delete(collectionCourse.rating)

	if not (collection.term is None or collectionCourse.isCustom() or collection.term in collectionCourse.course.calendar_terms):
		response["warnings"].append(f"Course {collectionCourse.course.code} was not available in this term's calendar")
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
	if "rating" in data:
		if collection.transfer:
			return {"error": "Cannot set rating for a transferred course"}, 400
		if not collection.isTaken():
			return {"error": "Cannot set rating for a course that has not been taken yet"}, 400
		try:
			collectionCourse.setRating(float(data["rating"]))
		except:
			return {"error": "Error setting rating"}, 400
	
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
	
	if collectionCourse.isCustom():
		customCourse = collectionCourse._custom_course
		try:
			db.session.delete(customCourse)
			db.session.commit()
		except:
			return {"error": "error deleting CustomCourse from CollectionCourse"}, 500

	try:
		db.session.delete(collectionCourse)
		db.session.commit()
	except:
		return {"error": "error deleting CollectionCourse"}, 500

	return {"success": True}, 200
