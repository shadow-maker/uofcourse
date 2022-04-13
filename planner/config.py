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


class MailConfig:
	def __init__(self, server="smtp.gmail.com", port=587, tls=True, user="", pssw=""):
		self.SERVER = getenv("MAIL_SERVER")
		if not self.SERVER:
			self.SERVER = server
	
		self.PORT = getenv("MAIL_PORT")
		if not self.PORT:
			self.PORT = port
		
		self.USE_TLS = getenv("MAIL_USE_TLS")
		if not self.USE_TLS:
			self.USE_TLS = tls

		self.USER = getenv("MAIL_USER")
		if not self.USER:
			self.USER = user

		self.PSSW = getenv("MAIL_PSSW")
		if not self.PSSW:
			self.PSSW = pssw

  
class Config:
	SECRET_KEY = getenv("SECRET_KEY")
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	SQLALCHEMY_POOL_RECYCLE = 299
	SQLALCHEMY_POOL_TIMEOUT = 20

	def __init__(self, dbConfig=DatabaseConfig(), mailConfig=MailConfig()):
		self.dbConfig = dbConfig
		self.mailConfig = mailConfig
	
	@property
	def SQLALCHEMY_DATABASE_URI(self):
		return self.dbConfig.URI
	
	@property
	def MAIL_SERVER(self):
		return self.mailConfig.SERVER
	
	@property
	def MAIL_PORT(self):
		return self.mailConfig.PORT
	
	@property
	def MAIL_USE_TLS(self):
		return self.mailConfig.USE_TLS
	
	@property
	def MAIL_USERNAME(self):
		return self.mailConfig.USER
	
	@property
	def MAIL_PASSWORD(self):
		return self.mailConfig.PSSW
