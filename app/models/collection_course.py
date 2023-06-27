from app import db
from app.models import Course, CustomCourse, CourseRating

from sqlalchemy import select
from sqlalchemy.ext.hybrid import hybrid_property

class CollectionCourse(db.Model):
	__tablename__ = "collection_course"
	id = db.Column(db.Integer, primary_key=True)
	collection_id = db.Column(db.Integer, db.ForeignKey("collection.id"), nullable=False)
	course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=True)
	custom_course_id = db.Column(db.Integer, db.ForeignKey("custom_course.id"), nullable=True)

	grade_id = db.Column(db.Integer, db.ForeignKey("grade.id"))
	passed = db.Column(db.Boolean)

	def isCustom(self):
		return self.course_id is None
	
	@hybrid_property
	def course(self):
		if self.course_id is not None:
			return Course.query.get(self.course_id)
		if self.custom_course_id is not None:
			return CustomCourse.query.get(self.custom_course_id)
		return None

	@hybrid_property
	def course_code(self):
		return self.course.code
	
	@course_code.expression # type: ignore
	def course_code(cls):
		if cls.course_id is not None:
			return select(Course.code).where(Course.id == cls.course_id)
		if cls.custom_course_id is not None:
			return select(CustomCourse.code).where(CustomCourse.id == cls.custom_course_id)
		return None
	
	@hybrid_property
	def rating(self):
		return CourseRating.query.filter_by(course_id=self.course_id, user_id=self.collection.user_id, term_id=self.collection.term_id).first()
	
	def setRating(self, value: float, outof: int = 100):
		if self.rating is None:
			db.session.add(CourseRating(self.course_id, self.collection.user_id, self.collection.term_id, value, outof))
		else:
			self.rating.setRating(value, outof)
	
	def isCalendarAvailable(self):
		if self.isCustom():
			return True
		return self.collection.term is None or self.collection.term in self.course.calendar_terms
	
	def calendarURL(self):
		if self.isCustom() or self.collection.transfer:
			return ""
		return self.course.calendarURL(self.collection.term.calendar)

	@hybrid_property
	def user(self):
		return self.collection.user

	@hybrid_property
	def user_id(self):
		return self.collection.user_id

	def getWeightedGPV(self, precision=3):
		if self.grade and self.grade.gpv is not None:
			return round(float(self.grade.gpv * self.course.units), precision)
		return None

	@property
	def weightedGPV(self):
		return self.getWeightedGPV()

	@property
	def tags(self):
		return [tag for tag in self.course.tags if tag.user_id == self.collection.user_id]

	def __init__(self, collection_id, course_id=None, custom_course_id=None):
		self.collection_id = collection_id
		if course_id is not None:
			self.course_id = course_id
		elif custom_course_id is not None:
			self.custom_course_id = custom_course_id

	def __repr__(self):
		return f"COLLECTION_COURSE (#{self.id}): Collection {self.collection_id} - Course {self.course_id}"

	def __iter__(self):
		yield "id", self.id
		yield "collection_id", self.collection_id
		yield "custom", self.isCustom()
		yield "course_id", self.course_id
		yield "course_code", self.course.code
		yield "course_emoji", self.course.emoji
		yield "course_units", float(self.course.units)
		yield "grade_id", self.grade_id
		yield "passed", self.passed
		yield "weightedGPV", self.weightedGPV
		yield "calendar_available", self.isCalendarAvailable(),
		yield "calendar_url", self.calendarURL()
		yield "rating", self.rating.percent if self.rating else None
