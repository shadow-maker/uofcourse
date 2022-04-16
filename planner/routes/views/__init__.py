from planner import app
from planner import changelog as change
from planner.models import Role
from planner.constants import *
from flask import Blueprint

#
# Create view route blueprint with no url prefix
#

view = Blueprint("view", __name__, url_prefix="/")

#
# Define constants - to be passed to all HTML templates and can be accessed via Jinja2
#

constants = {
	"SITE_NAME" : SITE_NAME,
	"DEF_DESCRIPTION" : DEF_DESCRIPTION,
	"CURRENT_VERSION" : CURRENT_VERSION,
	"CURRENT_VERSION_BETA" : CURRENT_VERSION in change and change[CURRENT_VERSION]["beta"],
	"DEBUG" : app.debug,
	"GANALYTICS_ID" : app.config["GANALYTICS_ID"],
	"DISQUS_EMBED": DISQUS_EMBED,
	"COLORS" : COLORS_DARK,
	"DEFAULT_EMOJI" : DEFAULT_EMOJI,
	"ROLE_ADMIN": Role.admin,
	"ROLE_MOD": Role.moderator
}

@view.context_processor
def viewConstants():
	return constants

#
# Import all view routes
#

from planner.routes.views.main import *
from planner.routes.views.auth import *
from planner.routes.views.user import *
from planner.routes.views.course import *
from planner.routes.views.error import *

from planner.routes.views.admin import admin
