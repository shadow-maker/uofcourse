from app import app
from app import constants
from app.models import Role, Faculty
from flask import Blueprint

#
# Create view route blueprint with no url prefix
#

view: Blueprint = Blueprint("view", __name__, url_prefix="/")

#
# Constants passed to all HTML templates to be accessed via Jinja2
#

@view.context_processor
def viewConstants():
	return {**{k : v for k, v in constants.__dict__.items() if not k.startswith("__")}, **{
		"DEBUG": app.debug,
		"GANALYTICS_ID" : app.config["GANALYTICS_ID"],
		"GADSENSE_ID" : app.config["GADSENSE_ID"],
		"PROPELLER_ID" : app.config["PROPELLER_ID"],
		"ROLE_ADMIN": Role.admin,
		"ROLE_MOD": Role.moderator,
		"FACULTIES": Faculty.query.all()
	}}

#
# Import all view routes
#

from app.routes.views.main import *
from app.routes.views.auth import *
from app.routes.views.user import *
from app.routes.views.course import *
from app.routes.views.subject import *
from app.routes.views.faculty import *
