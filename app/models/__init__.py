# DEFINES ALL DB MODELS (SQL TABLES)

from app import db

#
# University data related models
#

from app.models.faculty import Faculty
from app.models.subject import Subject
from app.models.course import Course

from app.models.term import Season, Term

from app.models.grade import Grade

#
# User related models
#

from app.models.user import Role, User
from app.models.user_log import UserLogEvent, UserLog
from app.models.course_tag import CourseTag
from app.models.user_tag import UserTag
from app.models.user_course import UserCourse
from app.models.course_collection import CourseCollection

#
# Create all tables in database
#

db.create_all()
