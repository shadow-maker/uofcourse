from app import db
from app.constants import UNI_URL, DEFAULT_EMOJI

from flask.helpers import url_for

class Faculty(db.Model):
	__tablename__ = "faculty"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64))
	subdomain = db.Column(db.String(16))

	users = db.relationship("User", backref="faculty")
	subjects = db.relationship("Subject", backref="faculty")

	@property
	def url(self):
		return url_for("view.faculty", fac=(self.subdomain if self.subdomain else self.id))
	
	@property
	def url_uni(self):
		return UNI_URL.replace("www", self.subdomain) if self.subdomain else None

	def __repr__(self):
		return f"FACULTY {self.name} (#{self.id})"

	def __iter__(self):
		yield "id", self.id
		yield "name", self.name
		yield "url", self.url
		yield "url_uni", self.url_uni
