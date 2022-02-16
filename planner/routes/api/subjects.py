from planner.models import Subject
from planner.routes.api.utils import *

from flask import Blueprint, request

subject = Blueprint("subjects", __name__, url_prefix="/subjects")


#
# GET
#

@subject.route("", methods=["GET"])
def getSubjects():
	return getAll(Subject, request.args)

@subject.route("/<id>", methods=["GET"])
def getSubjectById(id):
	return apiById(Subject, id)

@subject.route("/code/<code>", methods=["GET"])
def getSubjectByCodes(code):
	subject = getSubjectByCode(code)
	if not subject:
		return {"error": f"Subject with code {code} does not exist"}, 404
	return dict(subject), 200