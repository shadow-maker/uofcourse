from planner import db, bcrypt
from planner.constants import DEFAULT_EMOJI, LETTER_TO_GPA
from planner.adminView import admin, adminModelView

from flask import request
from flask_login import UserMixin
from datetime import datetime, date, time

import requests
import json
import httpx

#
# TERMS DB
#

class Season(db.Model):
	__tablename__ = "season"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(16), nullable=False)
	terms = db.relationship("Term", backref="season")

	def __repr__(self):
		return f"SEASON {self.name} (#{self.id})"

class Term(db.Model):
	__tablename__ = "term"
	id = db.Column(db.Integer, primary_key=True)
	season_id = db.Column(db.Integer, db.ForeignKey("season.id"), nullable=False)
	year = db.Column(db.Integer, nullable=False)
	start = db.Column(db.Date)
	end = db.Column(db.Date)

	courseCollections = db.relationship("CourseCollection", backref="term")

	def isCurrent(self):
		return self.start and self.end and self.start <= date.today() <= self.end

	def hasEnded(self):
		if not self.end:
			return None
		return self.end < date.today()

	def __repr__(self):
		return f"TERM {self.season.name} {self.year} (#{self.id})"

#
# COURSE DB
#

class Faculty(db.Model):
	__tablename__ = "faculty"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64))
	emoji = db.Column(db.Integer, nullable=True, unique=False)

	users = db.relationship("User", backref="faculty")
	subjects = db.relationship("Subject", backref="faculty")

	def getEmoji(self, default=None):
		if self.emoji:
			return self.emoji
		return default

	def __repr__(self):
		return f"FACULTY {self.name} (#{self.id})"

	def __iter__(self):
		yield "id", self.id
		yield "name", self.name
		yield "emoji", self.emoji


class Subject(db.Model):
	__tablename__ = "subject"
	id = db.Column(db.Integer, primary_key=True)
	faculty_id = db.Column(db.Integer, db.ForeignKey("faculty.id"), nullable=False)
	code = db.Column(db.String(6), nullable=False, unique=True)
	name = db.Column(db.String(64))
	emoji = db.Column(db.Integer, nullable=True, unique=False)
	site = db.Column(db.String(64))

	courses = db.relationship("Course", backref="subject")

	def getEmoji(self, default=None):
		if self.emoji:
			return self.emoji
		return self.faculty.getEmoji(default)

	def __repr__(self):
		return f"SUBJECT {self.name} (#{self.id}) - {self.code}"

	def __iter__(self):
		yield "id", self.id
		yield "faculty_id", self.faculty_id
		yield "code", self.code
		yield "name", self.name
		yield "emoji", self.emoji
		yield "site", self.site


class Course(db.Model):
	__tablename__ = "course"
	id = db.Column(db.Integer, primary_key=True)
	subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)
	code = db.Column(db.Integer, nullable=False, unique=False)
	level = db.Column(db.Integer, nullable=False, unique=False)
	name = db.Column(db.String(256))
	emoji = db.Column(db.Integer, nullable=True, unique=False)
	units = db.Column(db.Numeric(4, 2))
	desc = db.Column(db.Text)
	prereqs = db.Column(db.Text)
	antireqs = db.Column(db.Text)

	userCourses = db.relationship("UserCourse", backref="course")

	def getEmoji(self, default=DEFAULT_EMOJI):
		if self.emoji:
			return self.emoji
		return self.subject.getEmoji(default)

	def __init__(self, subject_id, code, name, units, desc, prereqs, antireqs, emoji=None):
		self.subject_id = subject_id
		self.code = code
		self.level = code // 100
		self.name = name
		self.units = units
		self.desc = desc
		self.prereqs = prereqs
		self.antireqs = antireqs
		if emoji:
			self.emoji = emoji

	def __repr__(self):
		return f"COURSE {self.name} (#{self.id}) - {self.code}"
	
	def __iter__(self):
		yield "id", self.id
		yield "subject_id", self.subject_id
		yield "code", self.code
		yield "name", self.name
		yield "emoji", self.emoji
		yield "units", self.units
		yield "desc", self.desc
		yield "prereqs", self.prereqs
		yield "antireqs", self.antireqs
	
#
# USER DB
#

class Role(db.Model):
	__tablename__ = "role"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(16), nullable=False)
	users = db.relationship("User", backref="role")

	def __repr__(self):
		return f"Role (#{self.id}) {self.name}"


class User(db.Model, UserMixin):
	__tablename__ = "user"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(32))
	email = db.Column(db.String(64), nullable=False)
	passw = db.Column(db.String(64), nullable=False)
	
	role_id = db.Column(db.Integer, db.ForeignKey("role.id"), nullable=False, default=1)

	createdAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

	faculty_id = db.Column(db.Integer, db.ForeignKey("faculty.id"), nullable=False)
	entryYear = db.Column(db.Integer)
	neededUnits = db.Column(db.Numeric(3, 2))

	courseCollections = db.relationship("CourseCollection", backref="user")

	def __init__(self, id, email, passw, faculty_id):
		self.id = id
		self.email = email
		self.passw = bcrypt.generate_password_hash(passw).decode("utf-8")
		self.faculty_id = faculty_id

	def updatePassw(self, passw):
		self.passw = bcrypt.generate_password_hash(passw).decode("utf-8")
	
	def isMod(self):
		return self.role.id == 2

	def isAdmin(self):
		return self.role.id == 3

	def __repr__(self):

		return f"USER {self.name} (#{self.id})"

	def __iter__(self):
		yield "id", self.id
		yield "name", self.name
		yield "email", self.email
		yield "faculty", dict(self.faculty)
		yield "entryYear", self.entryYear
		yield "neededUnits", self.neededUnits


class CourseCollection(db.Model):
	__tablename__ = "course_collection"
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
	term_id = db.Column(db.Integer, db.ForeignKey("term.id"))
	transfer = db.Column(db.Boolean, nullable=False, default=False)

	userCourses = db.relationship("UserCourse", backref="collection")

	def getGPA(self, precision=3, conversion=LETTER_TO_GPA):
		points = 0
		accUnits = 0
		for uCouse in self.userCourses:
			units = float(uCouse.course.units)
			accUnits += units
			gpv = uCouse.getGPV(conversion)
			if not gpv:
				return None
			points += (gpv * units)
		if accUnits == 0:
			return None
		return round(points / accUnits, precision)

	def __init__(self, user_id, term_id=None):
		self.user_id = user_id
		if term_id:
			self.term_id = term_id
		else:
			self.transfer = True

	def __repr__(self):
		return f"COLLECTION (#{self.id}) : User {self.user_id} - " + ("Transfer" if self.transfer else f"Term {self.term_id}")


class UserCourse(db.Model):
	__tablename__ = "user_course"
	id = db.Column(db.Integer, primary_key=True)
	course_collection_id = db.Column(db.Integer, db.ForeignKey("course_collection.id"), nullable=False)
	course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)

	gradePercent = db.Column(db.Numeric(4, 2))
	gradeLetter = db.Column(db.String(2))
	passed = db.Column(db.Boolean)

	def getGPV(self, conversion=LETTER_TO_GPA):
		if not self.gradeLetter:
			return None
		return conversion[self.gradeLetter]

	def __init__(self, course_collection_id, course_id):
		self.course_collection_id = course_collection_id
		self.course_id = course_id

	def __repr__(self):
		return f"USER_COURSE (#{self.id}): CourseCollection {self.course_collection_id} - Course {self.course_id}"


db.create_all()

admin.add_view(adminModelView(User, db.session))
admin.add_view(adminModelView(Course, db.session))
admin.add_view(adminModelView(Subject, db.session))
admin.add_view(adminModelView(Faculty, db.session))
admin.add_view(adminModelView(Term, db.session))
admin.add_view(adminModelView(Season, db.session))
