from app import db
from app.datetime import datetime

from flask import request

from enum import Enum

import requests


class UserLogEvent(Enum):
	# 1X: Auth log events
	AUTH_LOGIN = 10
	AUTH_LOGOUT = 11
	AUTH_CHANGE_PASSW = 12


class UserLog(db.Model):
	__tablename__ = "user_log"
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
	event = db.Column(db.Enum(UserLogEvent), nullable=False)

	datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	ip = db.Column(db.String(32))

	@property
	def type(self):
		return self.event.name.split("_")[0]

	@property
	def name(self):
		return " ".join(self.event.name.split("_")[1:])

	@property
	def location(self):
		r = requests.get("http://ip-api.com/json/" + self.ip)
		if r.status_code == 200:
			data = r.json()
			if "lat" in data and "lon" in data:
				data["gmaps"] = f"https://www.google.com/maps/place/{data['lat']},{data['lon']}"
			return data
		return None
	
	def __init__(self, user_id, event, ip=None):
		self.user_id = user_id
		self.event = event
		if ip is None:
			self.ip = request.headers["X-Real-IP"] if "X-Real-IP" in request.headers else request.remote_addr
		else:
			self.ip = ip

	def delete(self):
		db.session.delete(self)
		db.session.commit()
	
	def __repr__(self):
		return f"UserLog(user_id={self.user_id}, event={self.event}, ip={self.ip}, datetime={self.datetime})"

	def __iter__(self):
		yield "id", self.id
		yield "user_id", self.user_id
		yield "datetime", self.datetime.isoformat()
		yield "event_type", self.type
		yield "event_name", self.name
		yield "ip", self.ip
