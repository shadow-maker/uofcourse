from planner.constants import SITE_NAME

from dotenv import load_dotenv
from os import getenv

import requests

load_dotenv()

class IFTTT:
	BASE_URL = "https://maker.ifttt.com/trigger/"

	def __init__(self, events, key=""):
		self.EVENTS = events
		self.KEY = getenv("IFTTT_KEY")
		if not self.KEY:
			self.KEY = key
	
	def post(self, event, data={}):
		url = self.BASE_URL + f"{event}/with/key/{self.KEY}"
		r = requests.post(url, json=data)
		return r
	
	def args(self, *args):
		return {f"value{i + 1}" : arg for i, arg in enumerate(args)}
	
	def message(self, body):
		return self.post(self.EVENTS["message"], self.args(
			f"[{SITE_NAME}] - New message received",
			body.replace("\n", "<br>")
		))
