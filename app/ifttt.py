from app.constants import SITE_NAME

import requests


class IFTTT:
	BASE_URL = "https://maker.ifttt.com/trigger/"

	def __init__(self, key: str, events: dict[str, str]):
		self.KEY = key
		self.EVENTS = events
	
	def post(self, event: str, data: dict = {}) -> requests.Response:
		url = self.BASE_URL + f"{event}/with/key/{self.KEY}"
		r = requests.post(url, json=data)
		return r
	
	def args(self, *args) -> dict[str, str]:
		return {f"value{i + 1}" : arg for i, arg in enumerate(args)}
	
	def message(self, body: str) -> requests.Response:
		return self.post(self.EVENTS["message"], self.args(
			f"[{SITE_NAME}] - New message received",
			body.replace("\n", "<br>")
		))
