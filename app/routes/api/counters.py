from app.models import Role, User
from app.routes.api.utils import *

from flask import Blueprint


counter = Blueprint("counters", __name__, url_prefix="/counters")

#
# GET
#

@counter.route("/users", methods=["GET"])
def getCountUsers():
	count = {r.name : User.query.filter_by(role=r).count() for r in Role}
	count["total"] = User.query.count()
	return count, 200
