from app import db

# Association table for many-to-many relationship between courses and user_tags

CourseTag = db.Table("course_tag",
	db.Column("user_tag_id", db.Integer, db.ForeignKey("user_tag.id"), nullable=False),
	db.Column("course_id", db.Integer, db.ForeignKey("course.id"), nullable=False)
)
