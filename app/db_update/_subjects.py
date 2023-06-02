from . import _courses, prints
from app.models import db, Calendar, Subject
from app.constants import REQUESTS_TIMEOUT

from bs4 import BeautifulSoup, ResultSet
import requests

def update(calendar: Calendar, facultyID: int, items: ResultSet):
	for s in items:
		# Get Subject code, skip if too short
		code = s.text.replace(" ", "")
		if len(code) < 3 or len(code) > 6 or not code.isupper():
			continue
		
		prints(4, f"SUBJECT '{code}'", False)

		# Get Subject sub-url (site)
		site = s["href"]

		# Request Subject page
		try:
			r = requests.get(calendar.url + site, timeout=REQUESTS_TIMEOUT)
			if r.status_code != 200:
				raise requests.exceptions.RequestException()
		except requests.exceptions.RequestException:
			# In case normal page does not work, request print page
			try:
				r = requests.get(calendar.url + "print_" + site, timeout=REQUESTS_TIMEOUT)
				if r.status_code != 200:
					raise requests.exceptions.RequestException()
			except requests.exceptions.RequestException:
				prints(0, "REQUEST FAILED")
				continue

		# Initialize BeautifulSoup
		soup = BeautifulSoup(r.text, features="html.parser")

		# Get Subject name data
		name = " ".join(soup.find(class_="page-title").text.strip().split(" ")[:-1])

		# Check for existing Subject
		subject = Subject.query.filter_by(code=code).first()

		if subject: # Update Subject attributes
			prints(0, f"ALREADY EXISTS (# {subject.id}), checking for changed values...")
			if subject.faculty_id != facultyID:
				prints(4, f"- faculty_id does not match: (db) {subject.faculty_id} != {facultyID}, updating...")
				#subject.faculty_id = facultyID
			if subject.name != name:
				prints(4, f"- name does not match: (db) {subject.name} != {name}, updating...")
				subject.name = name
			if subject.site != site:
				prints(4, f"- site does not match: (db) {subject.site} != {site}, updating...")
				subject.site = site
			if calendar not in subject.calendars:
				subject.calendars.append(calendar)
			subject.old =  calendar.version != "current/"
		else: # Create new Subject
			prints(0, "creating row...")
			subject = Subject(facultyID, code, name, site)
			subject.calendars.append(calendar)
			subject.old =  calendar.version != "current/"
			db.session.add(subject)
		db.session.commit()
		
		# Get all Course HTML elements (rows)
		courseItems = soup.find_all(class_="item-container")

		_courses.update(calendar, subject.id, courseItems)
