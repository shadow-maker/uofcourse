from planner.models import Faculty, Subject
from planner import queryUtils as utils
from planner.routes.api.utils import *
from planner.routes.api.subjects import getSubjects
from planner.routes.api.courses import getCourses

from flask import Blueprint, request

import json

faculty = Blueprint("faculties", __name__, url_prefix="/faculties")


#
# GET
#

@faculty.route("", methods=["GET"])
def getFaculties():
	return getAll(Faculty)


@faculty.route("/<id>", methods=["GET"])
def getFacultyById(id):
	return getById(Faculty, id)


@faculty.route("/<id>/subjects", methods=["GET"])
def getFacultySubjects(id):
	if not utils.getById(Faculty, id):
		return {"error": f"Faculty with id {id} does not exist"}, 404
	return getSubjects(faculties=[int(id)])


@faculty.route("/<id>/courses", methods=["GET"])
def getFacultyCourses(id):
	if not utils.getById(Faculty, id):
		return {"error": f"Faculty with id {id} does not exist"}, 404
	return getCourses(faculties=[int(id)])
