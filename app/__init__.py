from app.config import DatabaseConfig, Config
from app.constants import IFTTT_EVENTS
from app.ifttt import IFTTT

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_alchemydumps import AlchemyDumps
from flask_caching import Cache
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

from jinja2 import Environment as JinjaEnvironment

import os
import json

#
# Init Flask app
#

app = Flask(__name__)

dbConfig = DatabaseConfig()
config = Config(dbConfig)

app.config.from_object(config)

#
# Init extra objects
#

db = SQLAlchemy(app)

migrate = Migrate(app, db)

alchemydumps = AlchemyDumps(app, db)

ipcache = Cache(app, config={"CACHE_DEFAULT_TIMEOUT": 600})

bcrypt = Bcrypt(app)
loginManager = LoginManager(app)

jinja = JinjaEnvironment()

ifttt = IFTTT(IFTTT_EVENTS)

#
# Init extra utils
#

try:
	with open(os.path.join(app.static_folder, "changelog.json"), "r") as file:
		changelog = json.load(file)
except:
	changelog = []

#
# Import models and routes
#

from app import models, routes
