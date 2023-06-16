from app import db
# from app.models import Course, Term, User
from app.localdt import utc

from sqlalchemy.ext.hybrid import hybrid_property


class CourseRating(db.Model):
	__tablename__ = "course_rating"
	id = db.Column(db.Integer, primary_key=True)
	course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
	term_id = db.Column(db.Integer, db.ForeignKey("term.id"), nullable=False)

	percent = db.Column(db.Integer, nullable=False)									# 0-100
	datetime = db.Column(db.DateTime, nullable=False, default=utc.now)

	def __init__(self, course_id, user_id, term_id, percent):
		self.course_id = course_id
		self.user_id = user_id
		self.term_id = term_id
		self.setRating(percent)

	def setRating(self, value: float, outof: int = 100):
		if value < 0 or value > outof:
			raise ValueError(f"Rating value {value} is not in range 0-{outof}")

		interval = 100.0 / outof
		self.percent = int(value * interval)

	def getRating(self, outof: int = 100, decimals: int = 2) -> float:
		interval = outof / 100.0
		return round(self.percent * interval, decimals)
	
	@hybrid_property
	def rating(self) -> float:
		return self.getRating()
	
	def __repr__(self):
		return f"COURSE_RATING(#{self.id})"
