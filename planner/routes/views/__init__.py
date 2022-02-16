from flask import Blueprint
view = Blueprint("view", __name__, url_prefix="/")

from planner.routes.views.main import *
from planner.routes.views.auth import *
from planner.routes.views.user import *
from planner.routes.views.course import *
from planner.routes.views.error import *
