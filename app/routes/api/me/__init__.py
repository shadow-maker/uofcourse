from app.auth import login_required
from flask import Blueprint

me = Blueprint("me", __name__, url_prefix="/me")

# Validate login for all /api/me routes

@me.before_request
@login_required
def meBeforeRequest():
	pass

# Disable CORS

@me.after_request
def apiAfterRequest(response):
	response.headers.pop("Access-Control-Allow-Origin", None)
	return response

from app.routes.api.me.main import *
from app.routes.api.me.logs import *
from app.routes.api.me.sessions import *
from app.routes.api.me.tags import *
from app.routes.api.me.planner import *
from app.routes.api.me.collections import *
from app.routes.api.me.courses import *

me.register_blueprint(me_main)
me.register_blueprint(me_log)
me.register_blueprint(me_session)
me.register_blueprint(me_tag)
me.register_blueprint(me_planner)
me.register_blueprint(me_collection)
me.register_blueprint(me_course)
