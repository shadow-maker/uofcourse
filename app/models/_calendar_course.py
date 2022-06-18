from app import db

# Association table for many-to-many relationship between calendars and courses

CalendarCourse = db.Table("calendar_course",
	db.Column("calendar_id", db.Integer, db.ForeignKey("calendar.id"), nullable=False),
	db.Column("course_id", db.Integer, db.ForeignKey("course.id"), nullable=False)
)