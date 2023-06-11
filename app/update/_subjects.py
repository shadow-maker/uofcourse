from ._logger import logger
from ._courses import update as coursesUpdate
from app.models import db, Calendar, Subject
from app.constants import REQUESTS_TIMEOUT

from bs4 import BeautifulSoup, ResultSet
import requests

def update(calendar: Calendar, facultyID: int, items: ResultSet):
	logger.info(f"Found {len(items)} Subject items")
	for i, s in enumerate(items):
		# Get Subject code, skip if too short
		code = s.text.replace(" ", "").strip()
		if len(code) < 3 or len(code) > 6 or not code.isupper():
			logger.warning(f"Subject item {i} has invalid code '{code}' (skipping)")
			continue
		logger.debug(f"Reading Subject with code '{code}'")

		# Get Subject sub-url (site)
		site = s["href"]

		# Request Subject page
		try:
			r = requests.get(calendar.url + site, timeout=REQUESTS_TIMEOUT)
			if r.status_code != 200:
				raise requests.exceptions.RequestException()
		except requests.exceptions.RequestException:
			# In case normal page does not work, request print page
			logger.debug(f"Failed request for subject page '{calendar.url + site}', trying print page")
			try:
				r = requests.get(calendar.url + "print_" + site, timeout=REQUESTS_TIMEOUT)
				if r.status_code != 200:
					raise requests.exceptions.RequestException()
			except requests.exceptions.RequestException:
				logger.error(f"Failed request for subject (print) page '{calendar.url + 'print_' + site}' (skipping)")
				continue

		# Initialize BeautifulSoup
		soup = BeautifulSoup(r.text, features="html.parser")

		# Get Subject name data
		name = " ".join(soup.find(class_="page-title").text.strip().split(" ")[:-1])

		# Check for existing Subject
		subject = Subject.query.filter_by(code=code).first()

		if subject is not None: # Update Subject attributes
			logger.debug(f"Subject '{code}' (id {subject.id}) already exists, checking for changed values")
			if subject.faculty_id != facultyID:
				logger.debug(f"Subject faculty_id does not match: (db) {subject.faculty_id} != {facultyID} (updating)")
				subject.faculty_id = facultyID
			if subject.name != name:
				logger.debug(f"Subject name does not match: (db) {subject.name} != {name} (updating)")
				subject.name = name
			if subject.site != site:
				logger.debug(f"Subject site does not match: (db) {subject.site} != {site} (updating)")
				subject.site = site
			if calendar not in subject.calendars:
				logger.debug(f"Subject's calendars does not contain {calendar.schoolyear} (adding)")
				subject.calendars.append(calendar)
			subject.old = calendar.version != "current/"
			if subject.old:
				logger.debug(f"Subject is not current")
		else: # Create new Subject
			logger.debug(f"Subject '{code}' does not exist (creating)")
			try:
				subject = Subject(facultyID, code, name, site)
				subject.calendars.append(calendar)
				subject.old =  calendar.version != "current/"
				db.session.add(subject)
			except Exception as e:
				logger.error(f"Failed to create Subject with code '{code}':\n{e}")
			if subject.old:
				logger.debug(f"Subject is not current")
		try:
			db.session.commit()
		except Exception as e:
			logger.error(f"Failed to commit Subject with code '{code}':\n{e}")
		
		# Get all Course HTML elements (rows)
		courseItems = soup.find_all(class_="item-container")

		coursesUpdate(calendar, subject.id, courseItems)
