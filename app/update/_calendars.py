from . import _faculties, prints
from app.models import Calendar
from app.constants import REQUESTS_TIMEOUT

from bs4 import BeautifulSoup
import requests
import sys

def update(items: list[Calendar]):
	for calendar in items:
		prints(0, "\nGETTING DATA FROM CALENDAR VERSION: " + calendar.version)
		
		# Request page
		try:
			r = requests.get(calendar.faculties_url, timeout=REQUESTS_TIMEOUT)
			if r.status_code != 200:
				raise requests.exceptions.RequestException()
		except requests.exceptions.RequestException:
			sys.exit("  FAILED REQUEST FOR FACULTIES PAGE")

		# Initialize BeautifulSoup
		soup = BeautifulSoup(r.text, features="html.parser")

		# Get all Faculty HTML elements
		items = soup.find_all(class_="item-container")

		_faculties.update(calendar, items)
