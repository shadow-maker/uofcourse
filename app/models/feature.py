from app import db
from app.models._user_featurerequest import UserFeatureRequest
from app.localdt import utc, local
from app.auth import current_user

class FeatureRequest(db.model):
    __tablename__ = "feature_request"
    id = db.Column(db.integer, primary_key=True)
    user_id = db.Column(db.integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(256), nullable=False)
    body = db.Column(db.Text)
    datetime = db.Column(db.DateTime, nullable=False, default=utc.now)
    num_likes = db.Column(db.integer, primary_key=True)
    posted_by = db.relationship("User", secondary=UserFeatureRequest, backref="features_not_requested")

    def __init__(self, user_id, title, body):
        self.user_id = user_id
        self.title = title
        self.body = body
    
    @property
    def datetime_utc(self):
        return utc.localize(self.datatime)

    @property
    def datetime_utc(self):
        return local.normalize(self.datetime_utc)
    
    def __repr__(self):
        return f"Feature Request(id={self.id})"
    
    def __iter__(self):
        yield "id", self.id
        yield "author_id", self.user_id
        yield "title", self.title
        yield "body", self.body
        yield "datetime_utc", self.datetime_utc.isoformat()
        yield "datetime_local", self.datetime_local.isoformat()
        yield "num_likes", self.num_likes
        yield "posted_by", current_user in self.posted_by