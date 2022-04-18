from planner import db

from flask import request
from datetime import datetime

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

	ip = db.Column(db.String(32))
	datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

	@property
	def type(self):
		return self.event.name.split("_")[0]

	@property
	def name(self):
		return self.event.name.split("_")[1:]

	@property
	def location(self):
		r = requests.get("http://ip-api.com/json/" + self.ip)
		return r.json() if r.status_code == 200 else None
	
	def __init__(self, user_id, event, ip=None):
		self.user_id = user_id
		self.event = event
		self.ip = ip if ip != None else request.remote_addr

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