# These routes are meant to be used internally by AJAX calls

# TODO: Add try statements to db.session.commit()

from planner import db
from planner.models import Course, UserTag
from planner.auth import current_user, login_required

from planner.routes.api.utils import *

from flask import Blueprint, request

tag = Blueprint("tags", __name__, url_prefix="/tags")

#
# GET
#

# User UserTags

@tag.route("", methods=["GET"])
@login_required
def getUserTags():
	return {"tags": [dict(tag) for tag in current_user.tags]}, 200

# Course UserTags

@tag.route("/course/<id>", methods=["GET"])
@login_required
def getCourseTags(id):
	course = Course.query.filter_by(id=id).first()
	if not course:
		return {"error": f"Course with id {id} does not exist"}, 404
	return {"tags": [dict(tag) for tag in course.userTags if tag.user_id == current_user.id]}, 200


#
# POST
#

@tag.route("", methods=["POST"])
@login_required
def addUserTag(data={}):
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
	
	tag = UserTag(current_user.id, name, color)

	db.session.add(tag)
	
	db.session.commit()

	return {"success": "Tag created"}, 200

#
# PUT
#

@tag.route("", methods=["PUT"])
@login_required
def editUserTag(data={}):
	if not data:
		data = request.form.to_dict()
		if not data:
			return {"error": "no data provided"}, 400

	if not "tag_id" in data:
		return {"error": "no Tag id provided in data"}, 400
	
	tag = UserTag.query.filter_by(id=data["tag_id"]).first()
	if not tag:
		return {"error": f"Tag with id {data['tag_id']} does not exist"}, 404
	if tag.user_id != current_user.id:
		return {"error": f"User does not have access to this Tag"}, 403
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
		tag.name = data["name"]

	if "color" in data:
		try:
			color = int(data["color"])
		except:
			return {"error": "Tag color must be an integer"}, 400
		if color < 0 or color > 16777215:
			return {"error": "Tag color must be an integer between 0 and 16777215"}, 400
		tag.color = color

	db.session.commit()

	return {"success": "Tag edited"}, 200



@tag.route("/course", methods=["PUT"])
@login_required
def putCourseTag(data={}):
	if not data:
		data = request.form.to_dict()
		if not data:
			return {"error": "no data provided"}, 400

	if not "course_id" in data:
		return {"error": "no Course id provided in data"}, 400
	if not "tag_id" in data:
		return {"error": "no Tag id provided in data"}, 400

	course = Course.query.filter_by(id=data["course_id"]).first()
	if not course:
		return {"error": f"Course with id {data['course_id']} does not exist"}, 404

	tag = UserTag.query.filter_by(id=data["tag_id"]).first()
	if not tag:
		return {"error": f"Tag with id {data['tag_id']} does not exist"}, 404
	if tag.user_id != current_user.id:
		return {"error": f"User does not have access to this Tag"}, 403

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

@tag.route("", methods=["DELETE"])
@login_required
def deleteUserTag(data={}):
	if not data:
		data = request.form.to_dict()
		if not data:
			return {"error": "no data provided"}, 400

	if not "tag_id" in data:
		return {"error": "no Tag id provided in data"}, 400
	
	tag = UserTag.query.filter_by(id=data["tag_id"]).first()
	if not tag:
		return {"error": f"Tag with id {data['tag_id']} does not exist"}, 404
	if tag.user_id != current_user.id:
		return {"error": f"User does not have access to this Tag"}, 403
	if not tag.deletable:
		return {"error": "Tag is not deletable"}, 403

	db.session.delete(tag)
	
	db.session.commit()

	return {"success": "Tag deleted"}, 200
