from planner import changelog
from planner.constants import *
from flask import Blueprint
view = Blueprint("view", __name__, url_prefix="/")

constants = {
	"SITE_NAME": SITE_NAME,
	"CURRENT_VERSION": CURRENT_VERSION,
	"CURRENT_VERSION_BETA": changelog[CURRENT_VERSION]["beta"] if CURRENT_VERSION in changelog else False,
}

from planner.routes.views.main import *
from planner.routes.views.auth import *
from planner.routes.views.user import *
from planner.routes.views.course import *
