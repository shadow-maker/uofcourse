from . import TIMEOUT
from planner.constants import UNI_BASE_URL
from planner.models import db, Faculty, Subject, Course

from bs4 import BeautifulSoup
import requests
import sys

def update():
	facURL = "course-by-faculty.html"

	# Request page
	try:
		r = requests.get(UNI_BASE_URL + facURL, timeout=TIMEOUT)
	except:
		sys.exit(f"FAILED REQUEST FOR FACULTIES PAGE ({facURL})")
	
	# Initialize BeautifulSoup
	soup = BeautifulSoup(r.text, features="html.parser")

	# Get all Faculty HTML elements (rows)
	content = soup.find(id="ctl00_ctl00_pageContent")
	rows = content.find_all("tr", recursive=False)

	for f in rows:
		# Get Faculty name data
		name = f.find(class_="generic-title").text.strip()

		# Check for existing Faculty
		faculty = Faculty.query.filter_by(name=name).first()
		print(f"FACULTY '{name}'", end=" ")

		if faculty:
			print(f"ALREADY EXISTS (# {faculty.id}), skipping...")
		else: # Create new Faculty
			print("creating row...")
			faculty = Faculty(name=name)
			db.session.add(faculty)
			db.session.commit()

		# Get all Subject links
		subjects = f.find(class_="generic-body").find_all("a")

		for s in subjects:
			# Get Subject code, skip if too short
			code = s.text.replace(" ", "")
			if len(code) < 3:
				continue
			
			# Get Subject sub-url (site)
			url = s["href"]

			print(f"  SUBJECT '{code}'", end=" ")

			# Request Subject page
			try:
				r = requests.get(UNI_BASE_URL + url, timeout=TIMEOUT)
			except requests.exceptions.RequestException:
				# In case normal page does not work, request print page
				try:
					r = requests.get(UNI_BASE_URL + "print_" + url, timeout=TIMEOUT)
				except requests.exceptions.RequestException:
					print("REQUEST FAILED")
					continue

			# Initialize BeautifulSoup
			soup = BeautifulSoup(r.text, features="html.parser")
	
			# Get Subject name data
			name = " ".join(soup.find(class_="page-title").text.strip().split(" ")[:-1])
	
			# Check for existing Subject
			subject = Subject.query.filter_by(code=code).first()

			if subject: # Update Subject attributes
				print(f"ALREADY EXISTS (# {subject.id}), checking for changed values...")
				if subject.faculty_id != faculty.id:
					print(f"  - facId does not match: (db) {subject.faculty_id} != {faculty.id}, updating...")
					subject.faculty_id = faculty.id
				if subject.name != name:
					print(f"  - name does not match: (db) {subject.name} != {name}, updating...")
					subject.name = name
				if subject.site != url:
					print(f"  - site does not match: (db) {subject.site} != {url}, updating...")
					subject.site = url
			else: # Create new Subject
				print("creating row...")
				subject = Subject(faculty.id, code, name, url)
				db.session.add(subject)
			db.session.commit()

			# Get page content
			content = soup.find(id="ctl00_ctl00_pageContent")
		
			# Get element ids for every course
			courseLinks = {}
			for link in content.find(id="ctl00_ctl00_pageContent_ctl00_ctl02_cnBody").find_all("a"):
				try:
					courseLinks[int(link.text.split(" ")[-1])] = link["href"].split("#")[-1]
				except:
					continue
			
			# Get all Course HTML elements (rows)
			rows = content.find_all("tr", recursive=False)
			
			for c in rows:
				# Skip invalid rows
				if not c.find_all("table"):
					continue
				
				# Get Course number and name data
				_, number, name = [i.text for i in c.find_all(class_="course-code")]
				number = int(number.replace(" ", ""))
				name = name.strip()

				print(f"    COURSE '{number}'", end=" ")

				# Get units data
				try:
					units = round(float(c.find(class_="course-hours").text.split(" ")[0]), 2)
				except:
					units = 0

				# Get desc data
				desc = c.find(class_="course-desc")
				if desc:
					desc = desc.text.strip()
				
				# Get prereqs data
				prereqs = c.find(class_="course-prereq")
				if prereqs:
					prereqs = prereqs.text.strip()

				# Get coreqs data
				coreqs = c.find(class_="course-coreq")
				if coreqs:
					coreqs = coreqs.text.strip()

				# Get antireqs data
				antireqs = c.find(class_="course-antireq")
				if antireqs:
					antireqs = antireqs.text.strip()
				
				# Get notes data
				notes = c.find(class_="course-notes")
				if notes:
					notes = notes.text.strip()

				# Get aka data
				aka = c.find(class_="course-aka")
				if aka:
					aka = aka.text.strip().replace("(", "").replace(")", "").capitalize()
				
				# Get repeat data
				repeatText = c.find(class_="course-repeat")
				if repeatText:
					repeatText = repeatText.text.strip()
					if repeatText:
						notes += "\n" if notes else ""
						notes += repeatText
				repeat = bool(repeatText)
				
				# Get nogpa data
				nogpaText = c.find(class_="course-nogpa")
				if nogpaText:
					nogpaText = nogpaText.text.strip()
					if nogpaText:
						notes += "\n" if notes else ""
						notes += nogpaText
				nogpa = bool(nogpaText)

				# Get subsite data
				subsite = None
				if number in courseLinks:
					subsite = courseLinks[number]
				
				# Check for existing Course
				course = Course.query.filter_by(subject_id=subject.id, number=number).first()

				if course: # Update Course attributes
					print(f"ALREADY EXISTS (# {course.id}), checking for changed values...")
					if course.subject_id != subject.id:
						print(f"    - subjId does not match: (db) {course.subject_id} != {subject.id}, updating...")
						course.subject_id = subject.id
					if course.name != name:
						print(f"    - name does not match: (db) {course.name} != {name}, updating...")
						course.name = name
					if course.desc != desc:
						print(f"    - desc does not match: (db) {course.desc} != {desc}, updating...")
						course.desc = desc
					if course.prereqs != prereqs:
						print(f"    - prereqs does not match: (db) {course.prereqs} != {prereqs}, updating...")
						course.prereqs = prereqs
					if course.coreqs != coreqs:
						print(f"    - coreqs does not match: (db) {course.coreqs} != {coreqs}, updating...")
						course.coreqs = coreqs
					if course.antireqs != antireqs:
						print(f"    - antireqs does not match: (db) {course.antireqs} != {antireqs}, updating...")
						course.antireqs = antireqs
					if course.notes != notes:
						print(f"    - notes does not match: (db) {course.notes} != {notes}, updating...")
						course.notes = notes
					if course.aka != aka:
						print(f"    - aka does not match: (db) {course.aka} != {aka}, updating...")
						course.aka = aka
					if course.repeat != repeat:
						print(f"    - repeat does not match: (db) {course.repeat} != {repeat}, updating...")
						course.repeat = repeat
					if course.nogpa != nogpa:
						print(f"    - nogpa does not match: (db) {course.nogpa} != {nogpa}, updating...")
						course.nogpa = nogpa
					if course.subsite != subsite:
						print(f"    - subsite does not match: (db) {course.subsite} != {subsite}, updating...")
						course.subsite = subsite
				else: # Create new course
					print("creating row...")
					course = Course(subject.id, number, name, units)
					course.desc = desc
					course.prereqs = prereqs
					course.coreqs = coreqs
					course.antireqs = antireqs
					course.notes = notes
					course.aka = aka
					course.repeat = repeat
					course.nogpa = nogpa
					course.subsite = subsite
					db.session.add(course)
				db.session.commit()
