from . import logger
from app import db
from app.models import Grade, Calendar
from app.constants import REQUESTS_TIMEOUT
from bs4 import BeautifulSoup

import requests
import sys

def update():
	print("\n" + ("-" * 20) + "UPDATING GRADES" + ("-" * 20) + "\n")

	calendar = Calendar.getLatest()

	logger.info("Updating GRADE table")
	logger.info(f"Using {calendar.schoolyear} calendar (latest)")

	# Request page
	try:
		r = requests.get(calendar.grades_url, timeout=REQUESTS_TIMEOUT)
	except requests.exceptions.RequestException:
		sys.exit(f"FAILED REQUEST FOR GRADE SYSTEM PAGE ({calendar.grades_page})")
	soup = BeautifulSoup(r.text, features="html.parser")

	# Get all grade rows
	content = soup.find(id="ctl00_ctl00_pageContent")
	table = content.find("tbody")
	rows = table.find_all("tr")[1:]
	logger.debug(f"Found {len(rows)} grade rows")

	for i, row in enumerate(rows):
		# Get and parse grade data
		logger.debug(f"Parsing row {i + 1}")
		try:
			symbol, gpv, desc = [j.text.strip().split("\n")[0] for j in row.find_all("td")]
			gpv = float(gpv) if gpv else None
		except Exception as e:
			logger.warning(f"Could not parse row {i + 1} (skipping):\n{e}")
			pass

		# Check for existing grade
		grade = Grade.query.filter_by(symbol=symbol).first()

		if grade: # Update Grade attributes
			logger.debug(f"Grade with symbol '{symbol}' already exists")
			if (float(grade.gpv) if grade.gpv != None else None) != gpv:
				logger.debug(f"Grade with symbol '{symbol}' gpv does not match: (db) {grade.gpv} != {gpv}, updating...")
				grade.gpv = gpv
			if grade.desc != desc:
				logger.debug(f"Grade with symbol '{symbol}' description does not match: (db) {grade.desc} != {desc}, updating...")
				grade.desc = desc
		else: # Create new Grade
			logger.debug(f"Creating grade with symbol '{symbol}'")
			try:
				grade = Grade(symbol, gpv, desc)
				db.session.add(grade)
			except Exception as e:
				logger.error(f"Could not create grade with symbol '{symbol}':\n{e}")
		try:
			db.session.commit()
		except Exception as e:
			logger.error(f"Could not commit grade with symbol '{symbol}':\n{e}")
			db.session.rollback()
			pass
	logger.info("Finished updating GRADE table")
