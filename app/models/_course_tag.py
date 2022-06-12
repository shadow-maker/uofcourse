from app import db

# Association table for many-to-many relationship between courses and tags

CourseTag = db.Table("course_tag",
	db.Column("tag_id", db.Integer, db.ForeignKey("tag.id"), nullable=False),
	db.Column("course_id", db.Integer, db.ForeignKey("course.id"), nullable=False)
)
