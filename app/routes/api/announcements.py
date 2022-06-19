from app import db
from app.models import Announcement
from app.auth import login_required, current_user
from app.routes.api.utils import *

from flask import Blueprint

import json


announcement = Blueprint("announcements", __name__, url_prefix="/announcements")

#
# GET
#

@announcement.route("", methods=["GET"])
def getAnnouncements():
	return getAll(Announcement)

@announcement.route("/<id>", methods=["GET"])
def getAnnouncement(id):
	return getById(Announcement, id)

#
# PUT
#

@announcement.route("/<id>/read", methods=["PUT"])
@login_required
def putAnnouncementRead(id, set=None):
	a = Announcement.query.get(id)
	if not a:
		return {"error": f"Announcement with id {id} does not exist"}, 404
	if set is None:
		data = request.json
		if not "set" in data:
			set = False
		elif data["set"] not in [True, False]:
			return {"error": "invalid 'set' value in data"}, 400
		else:
			set = data["set"]
	try:
		if set == True:
			current_user.read_announcements.append(a)
		elif set == False:
			current_user.read_announcements.remove(a)
		else:
			return {"error": "invalid 'set' value"}, 400
		db.session.commit()
	except:
		return {"error": "failed to set 'read' for announcement"}, 400
	return {
		"success": True,
		"read": a in current_user.read_announcements
	}, 200
