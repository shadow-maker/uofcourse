from app import db
from app.localdt import local

from enum import Enum


class Season(Enum):
	winter = 1
	spring = 2
	summer = 3
	fall = 4


class Term(db.Model):
	__tablename__ = "term"
	id = db.Column(db.Integer, primary_key=True)
	calendar_id = db.Column(db.Integer, db.ForeignKey("calendar.id"))
	season = db.Column(db.Enum(Season), nullable=False)
	year = db.Column(db.Integer, nullable=False)
	start = db.Column(db.Date)
	end = db.Column(db.Date)

	courseRatings = db.relationship("CourseRating", backref="term")
	collections = db.relationship("Collection", backref="term")

	@property
	def name(self):
		return f"{self.season.name} {self.year}"

	def isPrev(self, today=local.date()):
		return (self.year < today.year) if self.end is None else (self.end < today)

	def isCurrent(self, today=local.date()):
		return self.start and self.end and self.start <= today <= self.end
	
	def isNext(self, today=local.date()):
		return (self.year > today.year) if self.start is None else (self.start > today)
	
	@classmethod
	def getPrev(cls):
		today = local.date()
		for term in cls.query.order_by(cls.end.desc()).all():
			if term.isPrev(today):
				return term
		return None
	
	@classmethod
	def getCurrent(cls):
		today = local.date()
		for term in cls.query.order_by(cls.end.desc()).all():
			if term.isCurrent(today):
				return term
		return None

	@classmethod
	def getNext(cls):
		today = local.date()
		for term in cls.query.order_by(cls.start.asc()).all():
			if term.isNext(today):
				return term
		return None

	def __repr__(self):
		return f"TERM {self.season.name} {self.year} (#{self.id})"
	
	def __iter__(self):
		yield "id", self.id
		yield "season", self.season.name
		yield "year", self.year
		yield "start", self.start.isoformat() if self.start else None
		yield "end", self.end.isoformat() if self.end else None
		yield "prev", self.isPrev()
		yield "current", self.isCurrent()
		yield "next", self.isNext()
