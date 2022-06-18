from app import db
from app.constants import UNI_URL
from app.models._calendar_course import CalendarCourse
from app.models._calendar_subject import CalendarSubject

class Calendar(db.Model):
	__tablename__ = "calendar"

	mainpage = "pubs/calendar/"

	id = db.Column(db.Integer, primary_key=True)
	year = db.Column(db.Integer, nullable=False)
	version = db.Column(db.String(16), nullable=False)
	terms = db.relationship("Term", backref="calendar")

	courses = db.relationship("Course", secondary=CalendarCourse, backref="calendars")
	subjects = db.relationship("Subject", secondary=CalendarSubject, backref="calendars")

	def __init__(self, year, version):
		self.year = year
		self.version = version

	@property
	def url(self):
		return UNI_URL + self.mainpage + self.version

	@property
	def schoolyear(self):
		return f"{self.year}-{self.year + 1}"

	@classmethod
	def getLatest(cls):
		return cls.query.order_by(cls.year.desc()).first()

	def __repr__(self):
		return f"Calendar({self.schoolyear})"
