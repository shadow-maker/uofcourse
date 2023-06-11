from app import db
from app.constants import DEFAULT_EMOJI

from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property


class CustomCourse(db.Model):
	__tablename__ = "custom_course"
	id = db.Column(db.Integer, primary_key=True)
	subject_code = db.Column(db.String(6), nullable=False)
	number = db.Column(db.String(6), nullable=False)
	name = db.Column(db.String(256))
	emoji = db.Column(db.Integer, nullable=True, unique=False, default=DEFAULT_EMOJI)
	units = db.Column(db.Numeric(precision=4, scale=2), default=3.0) # 2 integer places, 2 decimal places
	repeat = db.Column(db.Boolean, nullable=False, default=False)
	countgpa = db.Column(db.Boolean, nullable=False, default=True)

	collectionCourses = db.relationship("CollectionCourse", backref="_custom_course")

	@hybrid_property
	def code(self):
		return f"{self.subject_code}-{self.number}"
	
	@code.expression # type: ignore
	def code(cls):
		return func.concat(cls.subject_code.scalar_subquery(), "-", cls.number)

	def getEmoji(self, default=DEFAULT_EMOJI):
		if self.emoji:
			return self.emoji
		return default

	def getCollectionCourses(self, userId):
		return [cc for cc in self.collectionCourses if cc.collection.user_id == userId]

	def __init__(self, subject_code: str, number: str):
		self.subject_code = subject_code
		self.number = number

	def __repr__(self):
		return f"CUSTOM_COURSE {self.name} (#{self.id}) - {self.number}"
	
	def __iter__(self):
		yield "id", self.id
		yield "subject_code", self.subject_code
		yield "number", self.number
		yield "level", None
		yield "code", self.code
		yield "name", self.name
		yield "emoji", self.emoji
		yield "units", float(self.units)
		yield "repeat", self.repeat
		yield "countgpa", self.countgpa
