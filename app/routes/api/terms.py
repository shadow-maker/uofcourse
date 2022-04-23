from app.models import Term
from app.routes.api.utils import *

from flask import Blueprint

term = Blueprint("terms", __name__, url_prefix="/terms")


#
# GET
#

@term.route("", methods=["GET"])
def getTerms():
	return getAll(Term)

@term.route("/<id>", methods=["GET"])
def getTermById(id):
	return getById(Term, id)
