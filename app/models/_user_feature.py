from app import db

# Association table for many-to-many relationship between users and feature requests

UserFeature = db.Table("user_feature",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), nullable=False),
    db.Column("feature_id", db.Integer, db.ForeignKey("feature.id"), nullable=False))