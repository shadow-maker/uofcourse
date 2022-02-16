from planner.config import DatabaseConfig, Config

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate

app = Flask(__name__)

dbConfig = DatabaseConfig()
config = Config(dbConfig)
app.config.from_object(Config)

db = SQLAlchemy(app)

migrate = Migrate(app, db)

bcrypt = Bcrypt(app)
loginManager = LoginManager(app)

from datetime import datetime, timedelta
utcoffset = timedelta(hours=round(((datetime.now() - datetime.utcnow()).seconds / 3600) - 24))

from planner.routes import *

app.register_blueprint(api)
app.register_blueprint(main)
app.register_blueprint(auth)
app.register_blueprint(account)
app.register_blueprint(courses)
app.register_blueprint(error)
