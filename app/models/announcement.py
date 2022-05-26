from app import db
from app.models.user_announcement import UserAnnouncement
from app.localdt import utc


class Announcement(db.Model):
	__tablename__ = "announcement"
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
	title = db.Column(db.String(256), nullable=False)
	body = db.Column(db.Text)
	datetime = db.Column(db.DateTime, nullable=False, default=utc.now)
	read_by = db.relationship("User", secondary=UserAnnouncement, backref="read_announcements")

	def __init__(self, user_id, title, body):
		self.user_id = user_id
		self.title = title
		self.body = body

	def __repr__(self):
		return f"Announcement(id={self.id}"
	
	def __iter__(self):
		yield "id", self.id
		yield "author_id", self.user_id
		yield "title", self.title
		yield "body", self.body
		yield "datetime", self.datetime.isoformat()
