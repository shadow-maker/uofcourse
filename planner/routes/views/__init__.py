from planner import app
from planner import changelog as change
from planner.constants import *
from flask import Blueprint

view = Blueprint("view", __name__, url_prefix="/")

@view.context_processor
def viewConstants():
    return dict(
		SITE_NAME = SITE_NAME,
		CURRENT_VERSION = CURRENT_VERSION,
		CURRENT_VERSION_BETA = change[CURRENT_VERSION]["beta"] if CURRENT_VERSION in change else False,
		DEBUG = app.debug
	)

from planner.routes.views.main import *
from planner.routes.views.auth import *
from planner.routes.views.user import *
from planner.routes.views.course import *
