from planner import db, bcrypt
from planner.adminView import admin, adminModelView
from planner.constants import *

from flask import request
from flask_login import UserMixin
from datetime import datetime, date

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
	
	def __iter__(self):
		yield "id", self.id
		yield "season", self.season.name
		yield "year", self.year
		yield "start", self.start
		yield "end", self.end

#
# GRADE DB
#

class Grade(db.Model):
	__tablename__ = "grade"
	id = db.Column(db.Integer, primary_key=True)
	symbol = db.Column(db.String(2), nullable=False)
	gpv = db.Column(db.Numeric(4, 2))
	passed = db.Column(db.Boolean, nullable=False, default=True)
	desc = db.Column(db.String(256))

	userCourses = db.relationship("UserCourse", backref="grade")

	def __init__(self, symbol, gpv, desc, passed=True):
		self.symbol = symbol
		self.gpv = gpv
		self.desc = desc
		self.passed = passed

	def __repr__(self):
		return f"GRADE {self.symbol} ({self.gpv}) {'PASSED' if self.passed else 'FAILED'} (#{self.id})"

	def __iter__(self):
		yield "id", self.id
		yield "symbol", self.symbol
		yield "gpv", self.gpv
		yield "passed", self.passed
		yield "desc", self.desc

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
	notes = db.Column(db.Text)

	userCourses = db.relationship("UserCourse", backref="course")

	def getEmoji(self, default=DEFAULT_EMOJI):
		if self.emoji:
			return self.emoji
		return self.subject.getEmoji(default)

	def __init__(self, subject_id, code, name, units, desc="", prereqs="", antireqs="", notes="", emoji=None):
		self.subject_id = subject_id
		self.code = code
		self.level = code // 100
		self.name = name
		self.units = units
		self.desc = desc
		self.prereqs = prereqs
		self.antireqs = antireqs
		self.notes = notes
		if emoji:
			self.emoji = emoji

	def __repr__(self):
		return f"COURSE {self.name} (#{self.id}) - {self.code}"
	
	def __iter__(self):
		yield "id", self.id
		yield "subject_id", self.subject_id
		yield "code", self.code
		yield "level", self.level
		yield "name", self.name
		yield "emoji", self.emoji
		yield "units", self.units
		yield "desc", self.desc
		yield "prereqs", self.prereqs
		yield "antireqs", self.antireqs
		yield "notes", self.notes
	
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
	ucid = db.Column(db.Integer, unique=True)
	name = db.Column(db.String(32))
	email = db.Column(db.String(64), nullable=False)
	passw = db.Column(db.String(64), nullable=False)
	
	role_id = db.Column(db.Integer, db.ForeignKey("role.id"), nullable=False, default=1)

	createdAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

	faculty_id = db.Column(db.Integer, db.ForeignKey("faculty.id"), nullable=False)
	entryYear = db.Column(db.Integer)
	neededUnits = db.Column(db.Numeric(3, 2))

	collections = db.relationship("CourseCollection", backref="user")
	tags = db.relationship("UserTag", backref="user")

	def __init__(self, ucid, name, email, passw, faculty_id):
		self.ucid = ucid
		self.name = name
		self.email = email
		self.passw = bcrypt.generate_password_hash(passw).decode("utf-8")
		self.faculty_id = faculty_id

		self.collections.append(CourseCollection(self.id))
		self.tags.append(UserTag(self.id, "Starred", STARRED_COLOR, STARRED_EMOJI))

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


course_tag = db.Table("course_tag",
	db.Column("user_tag_id", db.Integer, db.ForeignKey("user_tag.id"), nullable=False),
	db.Column("course_id", db.Integer, db.ForeignKey("course.id"), nullable=False)
)


class UserTag(db.Model):
	__tablename__ = "user_tag"
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
	name = db.Column(db.String(16), nullable=False)
	color = db.Column(db.Integer, nullable=False)
	emoji = db.Column(db.Integer)
	deletable = db.Column(db.Boolean, nullable=False, default=True)

	courses = db.relationship("Course", secondary=course_tag, backref="userTags")

	def __init__(self, user_id, name, color, emoji=None):
		self.user_id = user_id
		self.name = name
		self.color = color
		self.emoji = emoji


class CourseCollection(db.Model):
	__tablename__ = "course_collection"
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
	term_id = db.Column(db.Integer, db.ForeignKey("term.id"))
	transfer = db.Column(db.Boolean, nullable=False, default=False)

	userCourses = db.relationship("UserCourse", backref="collection")

	def getGPA(self, precision=3):
		points = 0
		accUnits = 0
		for uCouse in self.userCourses:
			grade = uCouse.grade
			if not grade:
				return None
			if grade.gpv:
				units = float(uCouse.course.units)
				accUnits += units
				points += float(grade.gpv) * units
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

	grade_id = db.Column(db.Integer, db.ForeignKey("grade.id"))
	passed = db.Column(db.Boolean)

	def ownedBy(self, user_id):
		return self.collection.user_id == user_id

	def getTags(self):
		return [tag for tag in self.course.userTags if tag.user_id == self.collection.user_id]

	def __init__(self, course_collection_id, course_id):
		self.course_collection_id = course_collection_id

	def __repr__(self):
		return f"USER_COURSE (#{self.id}): CourseCollection {self.course_collection_id} - Course {self.course_id}"
		

db.create_all()

admin.add_view(adminModelView(User, db.session))
admin.add_view(adminModelView(Grade, db.session))
admin.add_view(adminModelView(Course, db.session))
admin.add_view(adminModelView(Subject, db.session))
admin.add_view(adminModelView(Faculty, db.session))
admin.add_view(adminModelView(Term, db.session))
admin.add_view(adminModelView(Season, db.session))
