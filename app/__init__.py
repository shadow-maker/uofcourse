from app.config import Config
from app.constants import IFTTT_EVENTS
from app.ifttt import IFTTT

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_alchemydumps import AlchemyDumps
from flask_caching import Cache
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

from sqlalchemy.ext.declarative import DeclarativeMeta

from jinja2 import Environment as JinjaEnvironment

import os
import json

#
# Init Flask app
#

app = Flask(__name__)

cfg = Config()

app.config.from_object(cfg)

#
# Init extra objects
#

db: DeclarativeMeta = SQLAlchemy(app)


migrate = Migrate(app, db)

alchemydumps = AlchemyDumps(app, db)

ipcache = Cache(app, config={"CACHE_DEFAULT_TIMEOUT": 600})
ipcache2 = {}

bcrypt = Bcrypt(app)
loginManager = LoginManager(app)

jinja = JinjaEnvironment()

ifttt = IFTTT(app.config["IFTTT_KEY"], IFTTT_EVENTS)

#
# Init extra utils
#

try:
	static = app.static_folder
	fname = "changelog.json"
	with open(os.path.join(static, fname) if static else fname, "r") as file:
		changelog = json.load(file)
except:
	changelog = []

#
# Import models and routes
#

from app import models, routes
