from ._logger import logger
from ._faculties import update as facultiesUpdate
from app.models import Calendar
from app.constants import REQUESTS_TIMEOUT

from bs4 import BeautifulSoup
import requests
import sys

def update(items: list[Calendar]):
	logger.info(f"Found {len(items)} calendar items")
	for calendar in items:
		logger.info(f"Updating course data for calendar {calendar.schoolyear} version {calendar.version}")
		
		# Request page
		try:
			r = requests.get(calendar.faculties_url, timeout=REQUESTS_TIMEOUT)
			if r.status_code != 200:
				raise requests.exceptions.RequestException()
		except requests.exceptions.RequestException:
			logger.error(f"Failed request for faculties page ({calendar.faculties_url})")
			sys.exit("ERROR Failed request for faculties page")

		# Initialize BeautifulSoup
		soup = BeautifulSoup(r.text, features="html.parser")

		# Get all Faculty HTML elements
		items = soup.find_all(class_="item-container")

		facultiesUpdate(calendar, items)

		logger.info(
			f"Finished updating course data for calendar {calendar.schoolyear} version {calendar.version}, " +
			f"{len(calendar.courses)} courses found in this calendar"
		)
