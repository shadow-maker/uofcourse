from app import db

class Collection(db.Model):
	__tablename__ = "collection"
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
	term_id = db.Column(db.Integer, db.ForeignKey("term.id"))
	transfer = db.Column(db.Boolean, nullable=False, default=False)

	collectionCourses = db.relationship("CollectionCourse", backref="collection")

	@property
	def courses(self):
		return [cc.course for cc in self.collectionCourses]

	@property
	def units_total(self):
		return sum(float(cc.course.units) for cc in self.collectionCourses)

	@property
	def units_counted(self):
		return sum(
			float(cc.course.units) for cc in self.collectionCourses
			if cc.grade and cc.grade.gpv is not None
		)
	
	def getPoints(self, precision=3):
		points = 0
		for cc in self.collectionCourses:
			grade = cc.grade
			if grade is None:
				return None
			if cc.course.countgpa and grade.gpv is not None:
				points += float(grade.gpv) * float(cc.course.units)
		return round(points, precision)

	def getGPA(self, precision=3):
		points = self.getPoints(6)
		accUnits = self.units_counted
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
		for i in self.collectionCourses:
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
		yield "units", self.units_counted
		yield "gpa", self.gpa

	def __repr__(self):
		return f"COLLECTION (#{self.id}) : User {self.user_id} - " + ("Transfer" if self.transfer else f"Term {self.term_id}")
