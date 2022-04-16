from planner import db, bcrypt
from planner.constants import STARRED_COLOR, STARRED_EMOJI
from planner.models.user_tag import UserTag
from planner.models.course_collection import CourseCollection

from flask_login import UserMixin
from datetime import datetime

from enum import Enum


class Role(Enum):
	user = 1
	moderator = 2
	admin = 3

	def __lt__(self, other):
		return self.value < other.value
	
	def __le__(self, other):
		return self.value <= other.value

	def __gt__(self, other):
		return self.value > other.value
	
	def __ge__(self, other):
		return self.value >= other.value


class User(db.Model, UserMixin):
	__tablename__ = "user"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(32))
	email = db.Column(db.String(64), nullable=False)
	username = db.Column(db.String(16), unique=True)
	password = db.Column(db.String(64), nullable=False)
	role = db.Column(db.Enum(Role), nullable=False, default=Role.user)

	created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	
	faculty_id = db.Column(db.Integer, db.ForeignKey("faculty.id"), nullable=False)
	neededUnits = db.Column(db.Numeric(precision=5, scale=2)) # 3 integer places, 2 decimal places

	collections = db.relationship("CourseCollection", backref="user")
	tags = db.relationship("UserTag", backref="user")

	def __init__(self, uname, name, email, passw, faculty_id):
		self.username = uname
		self.name = name
		self.email = email
		self.password = bcrypt.generate_password_hash(passw).decode("utf-8")
		self.faculty_id = faculty_id

		self.collections.append(CourseCollection(self.id))

		starred = UserTag(self.id, "Starred", color=STARRED_COLOR, emoji=STARRED_EMOJI)
		starred.starred = True
		starred.deletable = False
		self.tags.append(starred)

	def checkPassw(self, passw):
		return bcrypt.check_password_hash(self.password, passw)

	def updatePassw(self, new):
		self.password = bcrypt.generate_password_hash(new).decode("utf-8")
	
	def delete(self):
		for tag in self.tags:
			tag.delete()
		for collection in self.collections:
			collection.delete()
		db.session.delete(self)

	def __repr__(self):
		return f"USER {self.name} (#{self.id})"

	def __iter__(self):
		yield "id", self.id
		yield "username", self.username
		yield "name", self.name
		yield "email", self.email
		yield "faculty", dict(self.faculty)
		yield "neededUnits", self.neededUnits
