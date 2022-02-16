from planner.models import Term
from planner.routes.api.utils import *

from flask import Blueprint, request

term = Blueprint("terms", __name__, url_prefix="/terms")


#
# GET
#

@term.route("", methods=["GET"])
def getTerms():
	return getAll(Term, request.args)

@term.route("/<id>", methods=["GET"])
def getTermById(id):
	return apiById(Term, id)