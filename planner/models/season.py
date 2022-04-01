from planner import db

class Season(db.Model):
	__tablename__ = "season"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(16), nullable=False)
	terms = db.relationship("Term", backref="season")

	def __repr__(self):
		return f"SEASON {self.name} (#{self.id})"

	def __iter__(self):
		yield "id", self.id
		yield "name", self.name
