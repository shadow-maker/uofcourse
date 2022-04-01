from planner import db

class Role(db.Model):
	__tablename__ = "role"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(16), nullable=False)
	users = db.relationship("User", backref="role")

	def __repr__(self):
		return f"Role (#{self.id}) {self.name}"
	
	def __iter__(self):
		yield "id", self.id
		yield "name", self.name
