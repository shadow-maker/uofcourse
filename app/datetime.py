from app.constants import TIMEZONE

from datetime import datetime, date, time
import pytz


# UTC Funcs

utc = pytz.timezone("UTC")

def utcnow():
	return datetime.now(utc)


# Local Time Funcs

class LocalDatetime:
	def __init__(self, zone):
		self.timezone = pytz.timezone(zone)

	def now(self):
		return datetime.now(self.timezone)

	def today(self):
		return self.now().date()

	def localize(self, dt):
		return self.timezone.localize(dt)

	def normalize(self, dt):
		return self.timezone.normalize(dt)

local = LocalDatetime(TIMEZONE)
