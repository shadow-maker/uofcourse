from planner import db

class Grade(db.Model):
	__tablename__ = "grade"
	id = db.Column(db.Integer, primary_key=True)
	symbol = db.Column(db.String(2), nullable=False)
	gpv = db.Column(db.Numeric(4, 2))
	passed = db.Column(db.Boolean, nullable=False, default=True)
	desc = db.Column(db.String(256))

	userCourses = db.relationship("UserCourse", backref="grade")

	def __init__(self, symbol, gpv, desc, passed=True):
		self.symbol = symbol
		self.gpv = gpv
		self.desc = desc
		self.passed = passed

	def __repr__(self):
		return f"GRADE {self.symbol} ({self.gpv}) {'PASSED' if self.passed else 'FAILED'} (#{self.id})"

	def __iter__(self):
		yield "id", self.id
		yield "symbol", self.symbol
		yield "gpv", float(self.gpv) if self.gpv else None
		yield "passed", self.passed
		yield "desc", self.desc
