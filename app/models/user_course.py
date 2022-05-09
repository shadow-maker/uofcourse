from app import db

class UserCourse(db.Model):
	__tablename__ = "user_course"
	id = db.Column(db.Integer, primary_key=True)
	course_collection_id = db.Column(db.Integer, db.ForeignKey("course_collection.id"), nullable=False)
	course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)

	grade_id = db.Column(db.Integer, db.ForeignKey("grade.id"))
	passed = db.Column(db.Boolean)

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
		return [tag for tag in self.course.userTags if tag.user_id == self.collection.user_id]

	def __init__(self, course_collection_id, course_id):
		self.course_collection_id = course_collection_id
		self.course_id = course_id

	def __repr__(self):
		return f"USER_COURSE (#{self.id}): CourseCollection {self.course_collection_id} - Course {self.course_id}"
