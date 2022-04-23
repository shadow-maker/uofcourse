from app import db

class CourseCollection(db.Model):
	__tablename__ = "course_collection"
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
	term_id = db.Column(db.Integer, db.ForeignKey("term.id"))
	transfer = db.Column(db.Boolean, nullable=False, default=False)

	userCourses = db.relationship("UserCourse", backref="collection")

	@property
	def units(self):
		return sum([float(uc.course.units) for uc in self.userCourses if uc.grade and uc.grade.gpv])
	
	def getPoints(self, precision=3):
		points = 0
		for uCouse in self.userCourses:
			grade = uCouse.grade
			if grade is None:
				return None
			if grade.gpv and not uCouse.course.nogpa:
				points += float(grade.gpv) * float(uCouse.course.units)
		return round(points, precision)

	def getGPA(self, precision=3):
		points = self.getPoints(6)
		accUnits = self.units
		if points is None or accUnits == 0:
			return None
		return round(points / accUnits, precision)

	@property
	def points(self):
		return self.getPoints()
	
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
		yield "points", self.points
		yield "units", self.units
		yield "gpa", self.gpa

	def __repr__(self):
		return f"COLLECTION (#{self.id}) : User {self.user_id} - " + ("Transfer" if self.transfer else f"Term {self.term_id}")
