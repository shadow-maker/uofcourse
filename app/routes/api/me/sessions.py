from flask import Blueprint, request, session

import json

me_session = Blueprint("sessions", __name__, url_prefix="/sessions")

#
# PUT
#

@me_session.route("/welcome", methods=["PUT"])
def putSessionWelcome():
	data = request.form.to_dict()
	if not "set" in data:
		if "welcome" in session and session["welcome"] == False:
			session["welcome"] = True
		else:
			session["welcome"] = False
	else:
		try:
			session["welcome"] = bool(json.loads(data["set"]))
		except:
			return {"error": "invalid 'set' value in data"}, 400
	return {"success": True}, 200

@me_session.route("/transferred", methods=["PUT"])
def putSessionTransferred():
	data = request.form.to_dict()
	if not "set" in data:
		if "transferred" in session and session["transferred"] == False:
			session["transferred"] = True
		else:
			session["transferred"] = False
	else:
		try:
			session["transferred"] = bool(json.loads(data["set"]))
		except:
			return {"error": "invalid 'set' value in data"}, 400
	return {"success": True}, 200
