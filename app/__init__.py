from app.config import Config
from app.constants import IFTTT_EVENTS, LOG_FORMAT, LOG_DATE_FORMAT
from app.localdt import utc
from app.ifttt import IFTTT

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_alchemydumps import AlchemyDumps
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

from sqlalchemy.ext.declarative import DeclarativeMeta
from jinja2 import Environment as JinjaEnvironment

import logging

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

bcrypt = Bcrypt(app)
loginManager = LoginManager(app)

jinja = JinjaEnvironment()

ifttt = IFTTT(app.config["IFTTT_KEY"], IFTTT_EVENTS)

ipcache : dict[str, dict] = {}

#
# Logging
#

LOG_LEVEL = logging.INFO

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)

logFormatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
logging.Formatter.converter = utc.converter()

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)

logger.addHandler(consoleHandler)

#
# Import models and routes
#

from app import models, routes, update
