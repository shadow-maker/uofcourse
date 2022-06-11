from app import db
from app.models import Course, Tag
from app.auth import current_user

from flask import Blueprint, request

me_tag = Blueprint("tags", __name__, url_prefix="/tags")

#
# GET
#

# User Tags

@me_tag.route("", methods=["GET"])
def getTags():
	return {"tags": [dict(tag) for tag in current_user.tags]}, 200

# Tag courses

@me_tag.route("/<id>/courses", methods=["GET"])
def getTagCourses(id):
	tag = Tag.query.filter_by(id=id, user_id=current_user.id).first()
	if not tag:
		return {"error": f"Tag with id {id} does not exist"}, 404
	return {
		"courses": [dict(course) for course in sorted(tag.courses, key=lambda course: course.code)]
	}, 200

# Course Tags

@me_tag.route("/course/<id>", methods=["GET"])
def getCourseTags(id):
	course = Course.query.get(id)
	if not course:
		return {"error": f"Course with id {id} does not exist"}, 404
	return {"tags": [dict(tag) for tag in course.tags if tag.user_id == current_user.id]}, 200


#
# POST
#

@me_tag.route("", methods=["POST"])
def addTag(data={}):
	if not data:
		data = request.form.to_dict()
		if not data:
			return {"error": "no data provided"}, 400
	
	if "name" not in data:
		return {"error": "no Tag name provided in data"}, 400
	if len(data["name"]) < 3:
		return {"error": "Tag name must be at least 3 characters long"}, 400
	if len(data["name"]) > 16:
		return {"error": "Tag name must be at most 16 characters long"}, 400
	for tag in current_user.tags:
		if tag.name == data["name"]:
			return {"error": "Tag name already exists"}, 400
	name = data["name"]

	if "color" not in data:
		return {"error": "no Tag color provided in data"}, 400
	try:
		color = int(data["color"])
	except:
		return {"error": "Tag color must be an integer"}, 400
	if color < 0 or color > 16777215:
		return {"error": "Tag color must be an integer between 0 and 16777215"}, 400

	try:
		tag = Tag(current_user.id, name, color)

		db.session.add(tag)	
		db.session.commit()
	except:
		return {"error": "Failed to add tag"}, 500

	return {"success": "Tag created"}, 200

#
# PUT
#

@me_tag.route("/<id>", methods=["PUT"])
def putTag(id, data={}):
	if not data:
		data = request.form.to_dict()
	
	tag = Tag.query.filter_by(id=id, user_id=current_user.id).first()
	if not tag:
		return {"error": f"Tag with id {data['tag_id']} does not exist"}, 404
	if not tag.deletable:
		return {"error": "Tag is not editable"}, 403
	
	if "name" in data:
		if len(data["name"]) < 3:
			return {"error": "Tag name must be at least 3 characters long"}, 400
		if len(data["name"]) > 16:
			return {"error": "Tag name must be at most 16 characters long"}, 400
		for t in current_user.tags:
			if t != tag and t.name == data["name"]:
				return {"error": "Tag name already exists"}, 400
		tag.name = data["name"].strip()

	if "color" in data:
		try:
			color = int(data["color"])
		except:
			return {"error": "Tag color must be an integer"}, 400
		if color < 0 or color > 16777215:
			return {"error": "Tag color must be an integer between 0 and 16777215"}, 400
		tag.color = color

	try:
		db.session.commit()
	except:
		return {"error": "Failed to edit tag"}, 500

	return {"success": "Tag edited"}, 200



@me_tag.route("/<id>/course/<course_id>", methods=["PUT"])
def putCourseTag(id, course_id):
	course = Course.query.get(course_id)
	if not course:
		return {"error": f"Course with id {course_id} does not exist"}, 404

	tag = Tag.query.filter_by(id=id, user_id=current_user.id).first()
	if not tag:
		return {"error": f"Tag with id {id} does not exist"}, 404

	if course in tag.courses:
		tag.courses.remove(course)
		msg = "Tag removed from Course"
	else:
		tag.courses.append(course)
		msg = "Tag added to Course"

	db.session.commit()

	return {"success": msg}, 200


#
# DELETE
#

@me_tag.route("/<id>", methods=["DELETE"])
def delTag(id):
	tag = Tag.query.filter_by(id=id, user_id=current_user.id).first()
	if not tag:
		return {"error": f"Tag with id {id} does not exist"}, 404
	if not tag.deletable:
		return {"error": "Tag is not deletable"}, 403

	db.session.delete(tag)
	db.session.commit()

	return {"success": "Tag deleted"}, 200
