from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate

import os
from dotenv import load_dotenv

load_dotenv()

user = "root"
pssw = ""
dbLocation = f"mysql://{user}:{pssw}@localhost/main"

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = dbLocation
db = SQLAlchemy(app)

migrate = Migrate(app, db)

bcrypt = Bcrypt(app)
loginManager = LoginManager(app)

from datetime import datetime, timedelta
utcoffset = timedelta(hours=round(((datetime.now() - datetime.utcnow()).seconds / 3600) - 24))

from planner import routes
