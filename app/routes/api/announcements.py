from flask_login import login_required
from app import db
from app.models import Announcement
from app.auth import current_user
from app.routes.api.utils import *

from flask import Blueprint


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
def putAnnouncementRead(id):
	a = Announcement.query.get(id)
	if not a:
		return {"error": f"Announcement with id {id} does not exist"}, 404
	current_user.read_announcements.append(a)
	db.session.commit()
	return {"success": True}, 200
