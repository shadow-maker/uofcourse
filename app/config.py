from dotenv import load_dotenv
from os import getenv

load_dotenv()

class DatabaseConfig:
	def __init__(self, type="mysql", address="localhost", name="main", user="root", pssw=""):
		self.TYPE = getenv("DB_TYPE")
		if not self.TYPE:
			self.TYPE = type

		self.ADDR = getenv("DB_ADDR")
		if not self.ADDR:
			self.ADDR = address

		self.NAME = getenv("DB_NAME")
		if not self.NAME:
			self.NAME = name

		self.USER = getenv("DB_USER")
		if not self.USER:
			self.USER = user

		self.PSSW = getenv("DB_PSSW")
		if not self.PSSW:
			self.PSSW = pssw
	
	@property
	def URI(self):
		return f"{self.TYPE}://{self.USER}:{self.PSSW}@{self.ADDR}/{self.NAME}"

  
class Config:
	SECRET_KEY = getenv("SECRET_KEY")
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	SQLALCHEMY_POOL_RECYCLE = 299
	SQLALCHEMY_POOL_TIMEOUT = 20

	GANALYTICS_ID = getenv("GANALYTICS_ID")
	GADSENSE_ID = getenv("GADSENSE_ID")

	def __init__(self, dbConfig=DatabaseConfig()):
		self.dbConfig = dbConfig
	
	@property
	def SQLALCHEMY_DATABASE_URI(self):
		return self.dbConfig.URI
