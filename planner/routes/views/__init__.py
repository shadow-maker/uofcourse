from planner import app
from planner import changelog as change
from planner.constants import *
from flask import Blueprint

view = Blueprint("view", __name__, url_prefix="/")

constants = dict(
	SITE_NAME = SITE_NAME,
	DEF_DESCRIPTION = DEF_DESCRIPTION,
	CURRENT_VERSION = CURRENT_VERSION,
	CURRENT_VERSION_BETA = change[CURRENT_VERSION]["beta"] if CURRENT_VERSION in change else False,
	DEBUG = app.debug,
	GANALYTICS_ID = GANALYTICS_ID,
	COLORS = COLORS_DARK
)

@view.context_processor
def viewConstants():
	return constants

from planner.routes.views.main import *
from planner.routes.views.auth import *
from planner.routes.views.user import *
from planner.routes.views.course import *
from planner.routes.views.error import *
