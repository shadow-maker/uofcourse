from flask import Blueprint

#
# Create view route blueprint with no url prefix
#

view: Blueprint = Blueprint("view", __name__, url_prefix="/")

#
# Import all view routes
#

from app.routes.views.main import *
from app.routes.views.auth import *
from app.routes.views.user import *
from app.routes.views.course import *
from app.routes.views.subject import *
from app.routes.views.faculty import *
