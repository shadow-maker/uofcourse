from dotenv import load_dotenv
from os import getenv

load_dotenv()

dbURI = lambda type, host, port, name, user, pssw: f"{type}://{user}:{pssw}@{host}:{port}/{name}"

class Config:
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	SQLALCHEMY_ENGINE_OPTIONS = {
		"pool_recycle": 280,
		"pool_timeout": 20
	}

	CACHE_TYPE = "SimpleCache"
	SESSION_TYPE = "filesystem"
	SESSION_FILE_DIR = "sessions"
	SESSION_PERMANENT = False
	SESSION_USE_SIGNER = True

	def __init__(self):
		for var in ["SECRET_KEY", "GANALYTICS_ID", "GADSENSE_ID", "PROPELLER_ID", "IFTTT_KEY", "LOG_LEVEL"]:
			setattr(self, var, getenv(var))

		self.SQLALCHEMY_DATABASE_URI = getenv("DB_URI")

		if not self.SQLALCHEMY_DATABASE_URI:
			self.SQLALCHEMY_DATABASE_URI = dbURI(
				getenv("DB_TYPE", "mysql"),
				getenv("DB_HOST", "localhost"),
				getenv("DB_PORT", "3306"),
				getenv("DB_NAME", "main"),
				getenv("DB_USER", "root"),
				getenv("DB_PSSW", "")
			)
