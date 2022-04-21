from planner import db

class CourseCollection(db.Model):
	__tablename__ = "course_collection"
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
	term_id = db.Column(db.Integer, db.ForeignKey("term.id"))
	transfer = db.Column(db.Boolean, nullable=False, default=False)

	userCourses = db.relationship("UserCourse", backref="collection")

	def getGPA(self, precision=3):
		points = 0
		accUnits = 0
		for uCouse in self.userCourses:
			if uCouse.course.nogpa:
				continue
			grade = uCouse.grade
			if not grade:
				return None
			if grade.gpv:
				units = float(uCouse.course.units)
				accUnits += units
				points += float(grade.gpv) * units
		if accUnits == 0:
			return None
		return round(points / accUnits, precision)
	
	@property
	def gpa(self):
		return self.getGPA()
	
	def delete(self):
		for i in self.userCourses:
			db.session.delete(i)
		db.session.delete(self)
		db.session.commit()

	def __init__(self, user_id, term_id=None):
		self.user_id = user_id
		if term_id:
			self.term_id = term_id
		else:
			self.transfer = True
	
	def __iter__(self):
		yield "id", self.id
		yield "user_id", self.user_id
		yield "term_id", self.term_id
		yield "transfer", self.transfer
		yield "gpa", self.gpa

	def __repr__(self):
		return f"COLLECTION (#{self.id}) : User {self.user_id} - " + ("Transfer" if self.transfer else f"Term {self.term_id}")
