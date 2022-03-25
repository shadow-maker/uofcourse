from os import getenv
from dotenv import load_dotenv

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
	
	def getURI(self):
		return f"{self.TYPE}://{self.USER}:{self.PSSW}@{self.ADDR}/{self.NAME}"

  
class Config:
	dbConfig = DatabaseConfig()

	SECRET_KEY = getenv("SECRET_KEY")
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	SQLALCHEMY_DATABASE_URI = dbConfig.getURI()
	SQLALCHEMY_POOL_RECYCLE = 299
	SQLALCHEMY_POOL_TIMEOUT = 20

	def __init__(self, dbConfig=None):
		if dbConfig:
			self.dbConfig = dbConfig
			self.SQLALCHEMY_DATABASE_URI = self.dbConfig.getURI()