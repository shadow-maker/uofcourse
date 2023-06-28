from app import db
from app.models import Calendar, Term, Subject
from app.constants import DEFAULT_EMOJI, MIN_RATINGS_NEEDED

from flask.helpers import url_for
from sqlalchemy import select, cast, func
from sqlalchemy.ext.hybrid import hybrid_property


class Course(db.Model):
	__tablename__ = "course"
	id = db.Column(db.Integer, primary_key=True)
	subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)
	number = db.Column(db.Integer, nullable=False, unique=False)
	name = db.Column(db.String(256))
	aka = db.Column(db.Text)
	units = db.Column(db.Numeric(precision=4, scale=2), default=3.0) # 2 integer places, 2 decimal places
	desc = db.Column(db.Text)
	prereqs = db.Column(db.Text)
	coreqs = db.Column(db.Text)
	antireqs = db.Column(db.Text)
	notes = db.Column(db.Text)
	repeat = db.Column(db.Boolean, nullable=False, default=False)
	countgpa = db.Column(db.Boolean, nullable=False, default=True)
	subsite = db.Column(db.String(32))
	old = db.Column(db.Boolean, nullable=False, default=False)

	ratings = db.relationship("CourseRating", backref="course")
	collectionCourses = db.relationship("CollectionCourse", backref="_course")

	lenRatingCache = None
	overallRatingCache = None

	@hybrid_property
	def faculty_id(self):
		return self.subject.faculty_id

	@faculty_id.expression # type: ignore
	def faculty_id(cls):
		return select(Subject.faculty_id).where(Subject.id == cls.subject_id)

	@hybrid_property
	def subject_code(self):
		return self.subject.code
	
	@subject_code.expression # type: ignore
	def subject_code(cls):
		return select(Subject.code).where(Subject.id == cls.subject_id)

	@hybrid_property
	def code(self):
		return f"{self.subject_code}-{self.number}"
	
	@code.expression # type: ignore
	def code(cls):
		return func.concat(cls.subject_code.scalar_subquery(), "-", cast(cls.number, db.String))

	@hybrid_property
	def level(self):
		return self.number // 100
	
	@level.expression # type: ignore
	def level(cls):
		return func.floor(cls.number / 100) # This might only work in MySQL and PostgreSQL
	
	def resetRatingCache(self):
		self.lenRatingCache = None
		self.overallRatingCache = None

	def getRatings(self, term: Term) -> list:
		if term not in self.calendar_terms:
			return self.ratings
		return [rating for rating in self.ratings if term.id == rating.term_id]
	
	def getRatingsDistribution(self, term: Term, outof: int = 100, decimals: int = 2) -> dict:
		ratings = self.getRatings(term)
		values = [rating.getRating(outof, decimals) for rating in ratings]
		distributions = {}
		for value in values:
			if value not in distributions:
				distributions[value] = 0
			distributions[value] += 1
		return distributions

	def getLenRating(self):
		if self.lenRatingCache is None:
			self.lenRatingCache = len(self.ratings)	
		return self.lenRatingCache
	
	def getLenTermRating(self, term: Term):
		if term not in self.calendar_terms:
			return None
		return len(self.getRatings(term))
	
	def getOverallRatingAveragePercent(self, minNeeded=MIN_RATINGS_NEEDED) -> float:
		if self.getLenRating() < minNeeded:
			return None
		if self.overallRatingCache is None:
			self.overallRatingCache = sum(r.percent for r in self.ratings) / self.getLenRating()
		return self.overallRatingCache

	def getOverallRatingAverage(self, minNeeded=MIN_RATINGS_NEEDED, outof: int = 100, decimals: int = 2) -> float:
		self.getOverallRatingAveragePercent(minNeeded)
		if self.overallRatingCache is None:
			return -1
		interval = outof / 100.0
		return round(self.overallRatingCache * interval, decimals)
	
	def getRatingAveragePercent(self, term: Term, minNeeded=MIN_RATINGS_NEEDED) -> float:
		if term not in self.calendar_terms:
			return None
		ratings = self.getRatings(term)
		if len(ratings) < minNeeded:
			return None
		return sum(r.percent for r in ratings) / len(ratings)

	def getRatingAverage(self, term: Term, minNeeded=MIN_RATINGS_NEEDED, outof: int = 100, decimals: int = 2) -> float:
		percent = self.getRatingAveragePercent(term, minNeeded)
		if percent is None:
			return -1
		interval = outof / 100.0
		return round(percent * interval, decimals)

	def latestCalendar(self) -> Calendar:
		return sorted(self.calendars, key=lambda cal: cal.year, reverse=True)[0]
	
	def calendarURL(self, calendar):
		if calendar not in self.calendars:
			return ""
		if self.subject.site:
			_url = calendar.url + self.subject.site
			if self.subsite:
				_url += "#" + self.subsite
			return _url
		return None
	
	def calendarLatestURL(self):
		return self.calendarURL(self.latestCalendar())

	@property
	def url(self):
		return url_for("view.course", subjectCode=self.subject.code, courseNumber=self.number)

	@property
	def url_uni(self):
		return self.calendarLatestURL()

	def getEmoji(self, default=DEFAULT_EMOJI):
		return self.subject.getEmoji(default)
	
	@property
	def emoji(self):
		return self.subject.getEmoji()

	@property
	def calendar_terms(self):
		return sorted([term for cal in self.calendars for term in cal.terms], key=lambda term: term.id, reverse=True)

	def getTags(self, userId):
		return [tag for tag in self.tags if tag.user_id == userId]
	
	def getCollectionCourses(self, userId):
		return [cc for cc in self.collectionCourses if cc.collection.user_id == userId]

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
		yield "units", float(self.units)
		yield "desc", self.desc
		yield "prereqs", self.prereqs
		yield "coreqs", self.coreqs
		yield "antireqs", self.antireqs
		yield "notes", self.notes
		yield "repeat", self.repeat
		yield "countgpa", self.countgpa
		yield "url", self.url
		yield "url_uni", self.url_uni
		yield "old", self.old
		yield "rating", self.getOverallRatingAverage()
