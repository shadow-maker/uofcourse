from app import db
from app.models.course_tag import CourseTag

class UserTag(db.Model):
	__tablename__ = "user_tag"
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
	name = db.Column(db.String(16), nullable=False)
	color = db.Column(db.Integer, nullable=False)
	emoji = db.Column(db.Integer)
	starred = db.Column(db.Boolean, nullable=False, default=False)
	deletable = db.Column(db.Boolean, nullable=False, default=True)

	courses = db.relationship("Course", secondary=CourseTag, backref="userTags")

	@property
	def color_hex(self):
		return f"{self.color:06x}"

	def __init__(self, user_id, name, color, emoji=None, deletable=True):
		self.user_id = user_id
		self.name = name
		self.color = color
		self.emoji = emoji
		self.deletable = deletable

	def delete(self):
		db.session.delete(self)
		db.session.commit()

	def __iter__(self):
		yield "id", self.id
		yield "user_id", self.user_id
		yield "name", self.name
		yield "color", self.color
		yield "color_hex", self.color_hex
		yield "emoji", self.emoji
		yield "starred", self.starred
		yield "deletable", self.deletable
	
	def __repr__(self):
		return f"UserTag (#{self.id}) : User {self.user_id} - {self.name}"
