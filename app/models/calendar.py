from app import db
from app.constants import UNI_URL
from app.models._calendar_course import CalendarCourse
from app.models._calendar_subject import CalendarSubject

class Calendar(db.Model):
	__tablename__ = "calendar"

	CALENDAR_PAGE = "pubs/calendar/"
	DEF_GRADES_PAGE = "f-1-1.html"
	DEF_FACULTIES_PAGE = "course-by-faculty.html"

	id = db.Column(db.Integer, primary_key=True)
	year = db.Column(db.Integer, nullable=False)
	version = db.Column(db.String(32), nullable=False)
	grades_page = db.Column(db.String(32), nullable=False, default=DEF_GRADES_PAGE)
	faculties_page = db.Column(db.String(32), nullable=False, default=DEF_FACULTIES_PAGE)

	terms = db.relationship("Term", backref="calendar")
	courses = db.relationship("Course", secondary=CalendarCourse, backref="calendars")
	subjects = db.relationship("Subject", secondary=CalendarSubject, backref="calendars")

	def __init__(self, year, version):
		self.year = year
		self.version = version

	@property
	def url(self):
		return UNI_URL + self.CALENDAR_PAGE + self.version
	
	@property
	def grades_url(self):
		return self.url + self.grades_page
	
	@property
	def faculties_url(self):
		return self.url + self.faculties_page

	@property
	def schoolyear(self):
		return f"{self.year}-{self.year + 1}"

	@classmethod
	def getLatest(cls):
		return cls.query.order_by(cls.year.desc()).first()

	def __repr__(self):
		return f"Calendar({self.schoolyear})"
