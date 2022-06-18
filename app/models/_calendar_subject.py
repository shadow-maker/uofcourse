from app import db

# Association table for many-to-many relationship between calendars and subjects

CalendarSubject = db.Table("calendar_subject",
	db.Column("calendar_id", db.Integer, db.ForeignKey("calendar.id"), nullable=False),
	db.Column("subject_id", db.Integer, db.ForeignKey("subject.id"), nullable=False)
)
