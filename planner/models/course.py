from planner import db
from planner.constants import DEFAULT_EMOJI

from flask.helpers import url_for

class Course(db.Model):
	__tablename__ = "course"
	id = db.Column(db.Integer, primary_key=True)
	subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)
	number = db.Column(db.Integer, nullable=False, unique=False)
	name = db.Column(db.String(256))
	aka = db.Column(db.Text)
	units = db.Column(db.Numeric(4, 2))
	desc = db.Column(db.Text)
	prereqs = db.Column(db.Text)
	coreqs = db.Column(db.Text)
	antireqs = db.Column(db.Text)
	notes = db.Column(db.Text)
	repeat = db.Column(db.Boolean, nullable=False, default=False)
	nogpa = db.Column(db.Boolean, nullable=False, default=False)
	subsite = db.Column(db.String(32))

	userCourses = db.relationship("UserCourse", backref="course")

	@property
	def code(self):
		return f"{self.subject.code}-{self.number}"
	
	@property
	def level(self):
		return self.number // 100
	
	@property
	def url(self):
		return url_for("view.course", subjectCode=self.subject.code, courseNumber=self.number)

	@property
	def url_uni(self):
		if self.subsite:
			return self.subject.url_uni + "#" + self.subsite
		return self.subject.url_uni

	def getEmoji(self, default=DEFAULT_EMOJI):
		if self.emoji:
			return self.emoji
		return self.subject.getEmoji(default)
	
	@property
	def emoji(self):
		return self.subject.getEmoji()
	
	def getTags(self, userId):
		return [tag for tag in self.userTags if tag.user_id == userId]
	
	def getUserCourses(self, userId):
		return [uc for uc in self.userCourses if uc.collection.user_id == userId]

	def __init__(self, subject_id, number, name, units):
		self.subject_id = subject_id
		self.number = number
		self.name = name
		self.units = units

	def __repr__(self):
		return f"COURSE {self.name} (#{self.id}) - {self.number}"
	
	def __iter__(self):
		yield "id", self.id
		yield "subject_id", self.subject_id
		yield "number", self.number
		yield "level", self.level
		yield "code", self.code
		yield "name", self.name
		yield "aka", self.aka
		yield "emoji", self.subject.emoji
		yield "units", self.units
		yield "desc", self.desc
		yield "prereqs", self.prereqs
		yield "coreqs", self.coreqs
		yield "antireqs", self.antireqs
		yield "notes", self.notes
		yield "repeat", self.repeat
		yield "nogpa", self.nogpa
		yield "url", self.url
		yield "url_uni", self.url_uni
