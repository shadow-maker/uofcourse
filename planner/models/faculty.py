from planner import db
from planner.constants import DEFAULT_EMOJI

from flask.helpers import url_for

class Faculty(db.Model):
	__tablename__ = "faculty"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64))
	emoji = db.Column(db.Integer, nullable=True, unique=False)

	users = db.relationship("User", backref="faculty")
	subjects = db.relationship("Subject", backref="faculty")

	@property
	def url(self):
		return url_for("view.faculty", facId=self.id)

	def getEmoji(self, default=DEFAULT_EMOJI):
		if self.emoji:
			return self.emoji
		return default

	def __repr__(self):
		return f"FACULTY {self.name} (#{self.id})"

	def __iter__(self):
		yield "id", self.id
		yield "name", self.name
		yield "emoji", self.emoji