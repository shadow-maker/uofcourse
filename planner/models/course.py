from planner import db
from planner.constants import DEFAULT_EMOJI

from flask.helpers import url_for

class Course(db.Model):
	__tablename__ = "course"
	id = db.Column(db.Integer, primary_key=True)
	subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)
	code = db.Column(db.Integer, nullable=False, unique=False)
	name = db.Column(db.String(256))
	emoji = db.Column(db.Integer, nullable=True, unique=False)
	units = db.Column(db.Numeric(4, 2))
	desc = db.Column(db.Text)
	prereqs = db.Column(db.Text)
	antireqs = db.Column(db.Text)
	notes = db.Column(db.Text)
	aka = db.Column(db.Text)

	userCourses = db.relationship("UserCourse", backref="course")

	@property
	def code_full(self):
		return f"{self.subject.code}-{self.code}"
	
	@property
	def level(self):
		return self.code // 100
	
	@property
	def url(self):
		return url_for("view.course", subjCode=self.subject.code, courseCode=self.code)

	def getEmoji(self, default=DEFAULT_EMOJI):
		if self.emoji:
			return self.emoji
		return self.subject.getEmoji(default)
	
	def getTags(self, userId):
		return [tag for tag in self.userTags if tag.user_id == userId]
	
	def getUserCourses(self, userId):
		return [uc for uc in self.userCourses if uc.collection.user_id == userId]

	def __init__(self, subject_id, code, name, units, desc="", prereqs="", antireqs="", notes="", aka="", emoji=None):
		self.subject_id = subject_id
		self.code = code
		self.name = name
		self.units = units
		self.desc = desc
		self.prereqs = prereqs
		self.antireqs = antireqs
		self.notes = notes
		self.aka = aka
		if emoji:
			self.emoji = emoji

	def __repr__(self):
		return f"COURSE {self.name} (#{self.id}) - {self.code}"
	
	def __iter__(self):
		yield "id", self.id
		yield "subject_id", self.subject_id
		yield "code", self.code
		yield "code_full", self.code_full
		yield "level", self.level
		yield "name", self.name
		yield "emoji", self.emoji
		yield "units", self.units
		yield "desc", self.desc
		yield "prereqs", self.prereqs
		yield "antireqs", self.antireqs
		yield "notes", self.notes
		yield "aka", self.aka
		yield "url", self.url
