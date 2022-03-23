from planner.config import DatabaseConfig, Config

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate

import os
import json

app = Flask(__name__)

dbConfig = DatabaseConfig()
config = Config(dbConfig)
app.config.from_object(Config)

db = SQLAlchemy(app)

migrate = Migrate(app, db)

bcrypt = Bcrypt(app)
loginManager = LoginManager(app)


try:
	with open(os.path.join(app.static_folder, "changelog.json"), "r") as file:
		changelog = json.load(file)
except:
	changelog = []


from datetime import datetime, timedelta
utcoffset = timedelta(hours=round(((datetime.now() - datetime.utcnow()).seconds / 3600) - 24))

from planner.routes.api import api
from planner.routes.views import view
from planner.routes.errors import error

app.register_blueprint(api)
app.register_blueprint(view)
app.register_blueprint(error)