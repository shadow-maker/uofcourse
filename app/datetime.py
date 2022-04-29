from app.constants import TIMEZONE

from datetime import datetime as dt
import pytz


class LocalDatetime:
	def __init__(self, zone):
		self.timezone = zone if issubclass(type(zone), pytz.tzinfo.BaseTzInfo) else pytz.timezone(zone)

	def now(self): # Gets the current datetime in the local timezone
		return dt.now(self.timezone)

	def date(self): # Gets the current date in the local timezone
		return self.now().date()
	
	def time(self): # Gets the current time in the local timezone
		return self.now().time()

	def localize(self, dt): # Adds timezone to an anaware datetime object
		return self.timezone.localize(dt)

	def normalize(self, dt): # Converts an aware datetime object into the local timezone
		return self.timezone.normalize(dt)
	
	def __repr__(self):
		return f"LocalDatetime(timezone={self.timezone})"


utc = LocalDatetime(pytz.utc)
local = LocalDatetime(TIMEZONE)
