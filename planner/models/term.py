from planner import db

from datetime import date

class Term(db.Model):
	__tablename__ = "term"
	id = db.Column(db.Integer, primary_key=True)
	season_id = db.Column(db.Integer, db.ForeignKey("season.id"), nullable=False)
	year = db.Column(db.Integer, nullable=False)
	start = db.Column(db.Date)
	end = db.Column(db.Date)

	courseCollections = db.relationship("CourseCollection", backref="term")

	@property
	def name(self):
		return f"{self.season.name} {self.year}"

	def isCurrent(self):
		return self.start and self.end and self.start <= date.today() <= self.end

	def hasEnded(self):
		if not self.end:
			return None
		return self.end < date.today()

	def __repr__(self):
		return f"TERM {self.season.name} {self.year} (#{self.id})"
	
	def __iter__(self):
		yield "id", self.id
		yield "season_id", self.season_id
		yield "season", self.season.name
		yield "year", self.year
		yield "start", self.start.isoformat() if self.start else None
		yield "end", self.end.isoformat() if self.end else None
