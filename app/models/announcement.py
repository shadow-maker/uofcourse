from app import db
from app.models.user_announcement import UserAnnouncement

class Announcement(db.Model):
	__tablename__ = "announcement"
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
	title = db.Column(db.String(256), nullable=False)
	body = db.Column(db.Text)

	read_by = db.relationship("User", secondary=UserAnnouncement, backref="read_announcements")

	def __init__(self, user_id, title, body):
		self.user_id = user_id
		self.title = title
		self.body = body

	def __repr__(self):
		return f"Announcement(#{self.id})"
