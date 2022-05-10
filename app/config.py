from dotenv import load_dotenv
from os import getenv

load_dotenv()

def dbURI(type, address, name, user, password):
	return f"{type}://{user}:{password}@{address}/{name}"

class Config:
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	SQLALCHEMY_ENGINE_OPTIONS = {
		"pool_recycle": 280,
		"pool_timeout": 20
	}

	CACHE_TYPE = "SimpleCache"

	def __init__(self):
		for var in ["SECRET_KEY", "GANALYTICS_ID", "GADSENSE_ID", "IFTTT_KEY"]:
			setattr(self, var, getenv(var))

		self.SQLALCHEMY_DATABASE_URI = getenv("DB_URI")
		if not self.SQLALCHEMY_DATABASE_URI:
			self.SQLALCHEMY_DATABASE_URI = dbURI(
				getenv("DB_TYPE", "mysql"),
				getenv("DB_ADDR", "localhost"),
				getenv("DB_NAME", "main"),
				getenv("DB_USER", "root"),
				getenv("DB_PSSW", "")
			)
