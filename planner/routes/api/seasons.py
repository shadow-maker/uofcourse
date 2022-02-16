from planner.models import Season
from planner.routes.api.utils import *

from flask import Blueprint, request

season = Blueprint("seasons", __name__, url_prefix="/seasons")


#
# GET
#

@season.route("", methods=["GET"])
def getSeasons():
	return getAll(Season, request.args)

@season.route("/<id>", methods=["GET"])
def getSeasonById(id):
	return getById(Season, id)