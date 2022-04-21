from app.models import Grade
from app.routes.api.utils import *

from flask import Blueprint

grade = Blueprint("grades", __name__, url_prefix="/grades")


#
# GET
#

@grade.route("", methods=["GET"])
def getGrades():
	return getAll(Grade)

@grade.route("/<id>", methods=["GET"])
def getGradeById(id):
	return getById(Grade, id)
