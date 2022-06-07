from app.models import User
from app.auth import current_user

from flask import Blueprint

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
		"courses_enrolled": current_user.coursesEnrolled,
		"units_taken": current_user.unitsTaken,
		"units_enrolled": current_user.unitsEnrolled,
		"units_needed": float(current_user.units) if current_user.units else None
	}, 200
