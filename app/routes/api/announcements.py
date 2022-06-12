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

@announcement.route("/<id>/read", methods=["GET"])
@login_required
def getAnnouncementRead(id):
	a = Announcement.query.get(id)
	if not a:
		return {"error": f"Announcement with id {id} does not exist"}, 404
	return {"read": a in current_user.read_announcements}, 200

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
		data = request.form.to_dict()
		if not "set" in data:
			set = False
		else:
			try:
				set = bool(json.loads(data["set"]))
			except:
				return {"error": "invalid 'set' value in data"}, 400
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
