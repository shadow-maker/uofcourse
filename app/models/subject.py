from app import db
from app.constants import UNI_CAL_URL, DEFAULT_EMOJI

from flask.helpers import url_for

class Subject(db.Model):
	__tablename__ = "subject"
	id = db.Column(db.Integer, primary_key=True)
	faculty_id = db.Column(db.Integer, db.ForeignKey("faculty.id"), nullable=False)
	code = db.Column(db.String(6), nullable=False, unique=True)
	name = db.Column(db.String(64))
	emoji = db.Column(db.Integer, nullable=True, unique=False)
	site = db.Column(db.String(64))

	courses = db.relationship("Course", backref="subject")

	@property
	def url(self):
		return url_for("view.subject", subjectCode=self.code)
	
	@property
	def url_uni(self):
		return UNI_CAL_URL + self.site if self.site else None

	def getEmoji(self, default=DEFAULT_EMOJI):
		if self.emoji:
			return self.emoji
		return default
	
	def setEmoji(self, emoji):
		if type(emoji) == int:
			self.emoji = emoji
		elif type(emoji) == str and emoji.isdigit():
			self.emoji = int(emoji)
		elif type(emoji) == str and len(emoji) == 1:
			self.emoji = ord(emoji)
		else:
			self.emoji = None
	
	def __init__(self, faculty_id, code, name, site="", emoji=None):
		self.faculty_id = faculty_id
		self.code = code.upper()
		self.name = name
		self.site = site
		self.setEmoji(emoji)

	def __repr__(self):
		return f"SUBJECT {self.name} (#{self.id}) - {self.code}"

	def __iter__(self):
		yield "id", self.id
		yield "faculty_id", self.faculty_id
		yield "code", self.code
		yield "name", self.name
		yield "emoji", self.emoji
		yield "url", self.url
		yield "url_uni", self.url_uni
