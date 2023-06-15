from app import db
from app.auth import current_user

from flask import Blueprint, request

me_main = Blueprint("main", __name__, url_prefix="/")

#
# GET
#

@me_main.route("")
def getMe():
	return dict(current_user), 200
