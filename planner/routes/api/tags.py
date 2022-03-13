# These routes are meant to be used internally by AJAX calls

# TODO: Add try statements to db.session.commit()

from planner import db
from planner.models import Course, User, UserTag
from planner.queryUtils import *
from planner.constants import *

from planner.routes.api.utils import *

from flask import Blueprint, request
from flask_login import current_user

import json

tag = Blueprint("tags", __name__, url_prefix="/tags")

#
# GET
#

# User UserTags

@tag.route("", methods=["GET"])
def getUserTags():
	if not current_user.is_authenticated:
		return {"error": "User not logged in"}, 401
	return {"tags": [dict(tag) for tag in current_user.tags]}, 200

# Course UserTags

@tag.route("/course/<id>", methods=["GET"])
def getCourseTags(id):
	if not current_user.is_authenticated:
		return {"error": "User not logged in"}, 401
	course = Course.query.filter_by(id=id).first()
	if not course:
		return {"error": f"Course with id {id} does not exist"}, 404
	return {"tags": [dict(tag) for tag in course.userTags if tag.user_id == current_user.id]}, 200


#
# PUT
#

@tag.route("/course", methods=["PUT"])
def putCourseTag(data={}):
	if not current_user.is_authenticated:
		return {"error": "User not logged in"}, 401
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

