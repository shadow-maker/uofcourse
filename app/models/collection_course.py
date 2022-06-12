from app import db
from app.models import Course

from sqlalchemy import select
from sqlalchemy.ext.hybrid import hybrid_property

class CollectionCourse(db.Model):
	__tablename__ = "collection_course"
	id = db.Column(db.Integer, primary_key=True)
	collection_id = db.Column(db.Integer, db.ForeignKey("collection.id"), nullable=False)
	course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)

	grade_id = db.Column(db.Integer, db.ForeignKey("grade.id"))
	passed = db.Column(db.Boolean)

	@hybrid_property
	def course_code(self):
		return self.subject.code
	
	@course_code.expression # type: ignore
	def course_code(cls):
		return select(Course.code).where(Course.id == cls.course_id)

	@property
	def user(self):
		return self.collection.user

	@property
	def user_id(self):
		return self.collection.user_id

	def getWeightedGPV(self, precision=3):
		if self.grade and self.grade.gpv:
			return round(float(self.grade.gpv * self.course.units), precision)
		return None

	@property
	def weightedGPV(self):
		return self.getWeightedGPV()

	@property
	def tags(self):
		return [tag for tag in self.course.tags if tag.user_id == self.collection.user_id]

	def __init__(self, collection_id, course_id):
		self.collection_id = collection_id
		self.course_id = course_id

	def __repr__(self):
		return f"USER_COURSE (#{self.id}): Collection {self.collection_id} - Course {self.course_id}"

	def __iter__(self):
		yield "id", self.id
		yield "collection_id", self.collection_id
		yield "course_id", self.course_id
		yield "course_code", self.course.code
		yield "course_emoji", self.course.subject.emoji
		yield "course_units", float(self.course.units)
		yield "grade_id", self.grade_id
		yield "passed", self.passed
		yield "weightedGPV", self.weightedGPV
