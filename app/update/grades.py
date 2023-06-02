from app import db
from app.models import Grade, Calendar
from app.constants import REQUESTS_TIMEOUT
from bs4 import BeautifulSoup

import requests
import sys

def update():
	print("\n" + ("-" * 20) + "UPDATING GRADES" + ("-" * 20) + "\n")

	calendar = Calendar.getLatest()

	print(f"* Using {calendar.schoolyear} (latest) calendar *\n")

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

	for i, row in enumerate(rows):
		# Get and parse grade data
		try:
			symbol, gpv, desc = [j.text.strip().split("\n")[0] for j in row.find_all("td")]
			if gpv:
				gpv = float(gpv)
			else:
				gpv = None
		except:
			print(f"ERROR: Could not parse row {i + 1}")
			pass

		# Check for existing grade
		grade = Grade.query.filter_by(symbol=symbol).first()

		if grade: # Update Grade attributes
			print(f"GRADE with symbol '{symbol}' ALREADY EXISTS")
			if (float(grade.gpv) if grade.gpv != None else None) != gpv:
				print(f"  - gpv does not match: (db) {grade.gpv} != {gpv}, updating...")
				grade.gpv = gpv
			if grade.desc != desc:
				print(f"  - description does not match: (db) {grade.desc} != {desc}, updating...")
				grade.desc = desc
			db.session.commit()
		else: # Create new Grade
			print(f"CREATING GRADE with symbol '{symbol}'")
			grade = Grade(symbol, gpv, desc)
			db.session.add(grade)
			db.session.commit()
