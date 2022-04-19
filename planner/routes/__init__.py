# DEFINE ALL APP ROUTES (used in views and for API)

from planner import app

from planner.routes.api import api
from planner.routes.views import view
from planner.routes.admin import admin

app.register_blueprint(api)
app.register_blueprint(view)
