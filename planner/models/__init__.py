# DEFINES ALL DB MODELS (SQL TABLES)

from planner import db

#
# University data related models
#

from planner.models.faculty import Faculty
from planner.models.subject import Subject
from planner.models.course import Course

from planner.models.season import Season
from planner.models.term import Term

from planner.models.grade import Grade

#
# User related models
#

from planner.models.user import Role, User
from planner.models.course_tag import CourseTag
from planner.models.user_tag import UserTag
from planner.models.user_course import UserCourse
from planner.models.course_collection import CourseCollection

#
# Create all tables in database
#

db.create_all()
