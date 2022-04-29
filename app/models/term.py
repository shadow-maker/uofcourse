from app import db

from enum import Enum
from app.datetime import local


class Season(Enum):
	winter = 1
	spring = 2
	summer = 3
	fall = 4


class Term(db.Model):
	__tablename__ = "term"
	id = db.Column(db.Integer, primary_key=True)
	season = db.Column(db.Enum(Season), nullable=False)
	year = db.Column(db.Integer, nullable=False)
	start = db.Column(db.Date)
	end = db.Column(db.Date)

	courseCollections = db.relationship("CourseCollection", backref="term")

	@property
	def name(self):
		return f"{self.season.name} {self.year}"

	def isPrev(self, today=local.today()):
		return self.end and self.end < today

	def isCurrent(self, today=local.today()):
		return self.start and self.end and self.start <= today <= self.end
	
	def isNext(self, today=local.today()):
		return self.start and self.start > today

	def __repr__(self):
		return f"TERM {self.season.name} {self.year} (#{self.id})"
	
	def __iter__(self):
		yield "id", self.id
		yield "season", self.season.name
		yield "year", self.year
		yield "start", self.start.isoformat() if self.start else None
		yield "end", self.end.isoformat() if self.end else None
