from planner.models import Term
from planner.routes.api.utils import *

from flask import Blueprint, request

faculty = Blueprint("faculties", __name__, url_prefix="/faculties")


#
# GET
#

@faculty.route("", methods=["GET"])
def getFaculties():
	return getAll(Faculty, request.args)

@faculty.route("/<id>", methods=["GET"])
def getFacultyById(id):
	return apiById(Faculty, id)