from app import db, bcrypt
from app import models
from app.constants import STARRED_COLOR, STARRED_EMOJI
from app.localdt import utc

from flask_login import UserMixin
from sqlalchemy import not_

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
	email = db.Column(db.String(64), nullable=False, unique=True)
	username = db.Column(db.String(16), nullable=False, unique=True)
	password = db.Column(db.String(64), nullable=False)
	role = db.Column(db.Enum(Role), nullable=False, default=Role.user)

	created = db.Column(db.DateTime, nullable=False, default=utc.now)
	
	faculty_id = db.Column(db.Integer, db.ForeignKey("faculty.id"), nullable=False)
	units = db.Column(db.Numeric(precision=5, scale=2), default=120) # 3 integer places, 2 decimal places

	collections = db.relationship("Collection", backref="user")
	tags = db.relationship("Tag", backref="user")
	announcements = db.relationship("Announcement", backref="author")
	features = db.relationship("FeatureRequest", backref="author")

	logs = db.relationship("UserLog", backref="user")

	def __init__(self, uname, name, email, passw, faculty_id):
		self.username = uname
		self.name = name
		self.email = email
		self.password = bcrypt.generate_password_hash(passw).decode("utf-8")
		self.faculty_id = faculty_id

		self.collections.append(models.Collection(self.id))

		starred = models.Tag(self.id, "Starred", color=STARRED_COLOR, emoji=STARRED_EMOJI)
		starred.starred = True
		starred.deletable = False
		self.tags.append(starred)

		self.read_announcements = models.Announcement.query.all()
		self.features_not_requested = models.FeatureRequest.query.all()

	@property
	def coursesTaken(self):
		return sum(
			len(collection.collectionCourses) for collection in self.collections
			if collection.transfer or collection.term.isPrev()
		)

	@property
	def coursesPlanned(self):
		return sum(len(collection.collectionCourses) for collection in self.collections)

	@property
	def unitsNeeded(self):
		return float(self.units) if self.units else None

	@property
	def unitsTaken(self):
		for collection in self.collections:
			print(collection, collection.transfer or collection.term.isPrev(), collection.units_total)
		return sum(
			collection.units_total for collection in self.collections
			if collection.transfer or collection.term.isPrev()
		)

	@property
	def unitsPlanned(self):
		return sum(
			collection.units_total for collection in self.collections
			if not(collection.transfer or collection.term.isPrev())
		)

	def log(self, event, ip=None):
		log = models.UserLog(self.id, event, ip)
		db.session.add(log)
		db.session.commit()
	
	def addTag(self, name, color, emoji=None, deletable=True):
		tag = models.Tag(self.id, name, color, emoji, deletable)
		self.tags.append(tag)
		db.session.commit()
		return tag
	
	def requestFeature(self, title, body):
		request = models.FeatureRequest(self.id, title, body)
		db.session.add(request)
		db.session.commit()
	
	@property
	def features_requested(self):
		return models.FeatureRequest.query.filter(
			(models.FeatureRequest.posted_by.contains(self))).order_by(models.FeatureRequest.datetime.desc()
		).all()
	
	def announce(self, title, body):
		announcement = models.Announcement(self.id, title, body)
		db.session.add(announcement)
		db.session.commit()
	
	@property
	def unread_announcements(self):
		return models.Announcement.query.filter(
			not_(models.Announcement.read_by.contains(self))).order_by(models.Announcement.datetime.desc()
		).all()

	def checkPassw(self, passw):
		return bcrypt.check_password_hash(self.password, passw)

	def updatePassw(self, new):
		self.password = bcrypt.generate_password_hash(new).decode("utf-8")
		self.log(models.UserLogEvent.AUTH_CHANGE_PASSW)
	
	def delete(self):
		for tag in self.tags:
			tag.delete()
		for collection in self.collections:
			collection.delete()
		for log in self.logs:
			log.delete()
		db.session.delete(self)

	def __repr__(self):
		return f"USER {self.name} (#{self.id})"

	def __iter__(self):
		yield "id", self.id
		yield "username", self.username
		yield "role", self.role.name
		yield "name", self.name
		yield "email", self.email
		yield "faculty_id", self.faculty_id
