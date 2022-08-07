# DEFINES ALL DB MODELS (SQL TABLES)

from app import db

#
# University data related models
#

from app.models.faculty import Faculty
from app.models.subject import Subject
from app.models.course import Course

from app.models.calendar import Calendar
from app.models.term import Season, Term

from app.models.grade import Grade

#
# User related models
#

from app.models.user import Role, User
from app.models.user_log import UserLogEvent, UserLog
from app.models.tag import Tag
from app.models.collection_course import CollectionCourse
from app.models.collection import Collection
from app.models.announcement import Announcement
from app.models.feature import Feature

#
# Create all tables in database
#

db.create_all()
