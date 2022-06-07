from app.models import UserLog
from app.auth import current_user
from app.routes.api.utils import getAll

from flask import Blueprint

me_log = Blueprint("logs", __name__, url_prefix="/logs")

#
# GET
#

@me_log.route("")
def getUserLogs():
	filters = (
		UserLog.user_id == current_user.id,
	)
	return getAll(UserLog, filters)


@me_log.route("/<id>")
def getUserLog(id):
	log = UserLog.query.filter_by(id=id, user_id=current_user.id).first()
	if not log:
		return {"error": "log not found"}, 404
	return dict(log), 200


@me_log.route("/<id>/location")
def getUserLogLocation(id):
	log = UserLog.query.filter_by(id=id, user_id=current_user.id).first()
	if not log:
		return {"error": "log not found"}, 404
	return log.location, 200
