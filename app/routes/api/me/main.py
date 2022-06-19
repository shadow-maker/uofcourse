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

@me_main.route("/progress")
def getProgress():
	return {
		"courses_taken": current_user.coursesTaken,
		"courses_planned": current_user.coursesPlanned,
		"units_taken": current_user.unitsTaken,
		"units_planned": current_user.unitsPlanned,
		"units_needed": current_user.unitsNeeded
	}, 200

#
# PUT
#

@me_main.route("/progress", methods=["PUT"])
def putUnitsNeeded(unitsNeeded=None):
	if unitsNeeded is None:
		try:
			unitsNeeded = float(request.json["units_needed"])
		except:
			return {"error": "invalid units_needed value"}, 400
	try:
		current_user.units = unitsNeeded
		db.session.commit()
	except:
		return {"error": "failed to update units needed"}, 400
	return {"success": True}, 200
