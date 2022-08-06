from dotenv import load_dotenv
from os import getenv

load_dotenv()

def dbURI(type, host, port, name, user, password):
	return f"{type}://{user}:{password}@{host}:{port}/{name}"

class Config:
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	SQLALCHEMY_ENGINE_OPTIONS = {
		"pool_recycle": 280,
		"pool_timeout": 20
	}
 # Test
	CACHE_TYPE = "SimpleCache"

	def __init__(self):
		for var in ["SECRET_KEY", "GANALYTICS_ID", "GADSENSE_ID", "PROPELLER_ID", "IFTTT_KEY"]:
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
