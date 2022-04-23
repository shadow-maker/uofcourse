# DEFINE ALL APP ROUTES (used in views and for API)

from app import app

from app.routes.api import api
from app.routes.views import view
from app.routes.admin import admin

app.register_blueprint(api)
app.register_blueprint(view)
