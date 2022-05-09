from app import db

# Association table for many-to-many relationship between users and announcements

UserAnnouncement = db.Table("user_announcement",
	db.Column("user_id", db.Integer, db.ForeignKey("user.id"), nullable=False),
	db.Column("announcement_id", db.Integer, db.ForeignKey("announcement.id"), nullable=False)
)
