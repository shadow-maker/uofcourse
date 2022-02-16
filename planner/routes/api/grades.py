from planner.models import Grade
from planner.routes.api.utils import *

from flask import Blueprint, request

grade = Blueprint("grades", __name__, url_prefix="/grades")


#
# GET
#

@grade.route("", methods=["GET"])
def getGrades():
	return getAll(Grade, request.args)

@grade.route("/<id>", methods=["GET"])
def getGradeById(id):
	return apiById(Grade, id)