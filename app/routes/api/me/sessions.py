from flask import Blueprint, request, session

import json

me_session = Blueprint("sessions", __name__, url_prefix="/sessions")

ALLOWED_SESSION_KEYS = [
	"welcome",
	"transferred"
]

#
# PUT
#

@me_session.route("/<key>", methods=["PUT"])
def putSessionKey(key):
	if key not in ALLOWED_SESSION_KEYS:
		return {"error": "invalid session key"}, 400
	data = request.json
	if not "set" in data:
		session[key] = key in session and session[key] == False
	elif data["set"] not in [True, False]:
		return {"error": "invalid 'set' value in data"}, 400
	else:
		session[key] = data["set"]
	return {"success": True}, 200
