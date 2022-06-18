from . import TIMEOUT, prints
from app.constants import UNI_CAL_URL, UNI_CAL_VERSIONS
from app.models import db, Faculty, Subject, Course

from bs4 import BeautifulSoup
import requests
import sys

facultyMaps = {
	"Faculty of Communication and Culture": "Faculty of Arts",
	"Faculty of Fine Arts": "Faculty of Arts",
	"Faculty of Humanities": "Faculty of Arts",
	"Faculty of Social Sciences": "Faculty of Arts",
	"Collaborating Faculties": "Faculty of Arts",
	"Faculty of Education": "Werklund School of Education",
	"Faculty of Medicine": "Cumming School of Medicine",
	"Faculty of Environmental Design": "School of Architecture, Planning and Landscape",
	"Architecture, Planning and Landscape, School of": "School of Architecture, Planning and Landscape",
	"Faculty of Veterniary Medicine": "Faculty of Veterinary Medicine"
}

def update():
	facURL = "course-by-faculty.html"

	for vIndex, version in enumerate(UNI_CAL_VERSIONS):
		print("\nGETTING FACULTY SUBJECTS FROM CALENDAR VERSION: " + version)

		url = UNI_CAL_URL + version + facURL

		# Request page
		try:

			r = requests.get(url, timeout=TIMEOUT)
			if r.status_code != 200:
				raise requests.exceptions.RequestException()
		except:
			sys.exit("  FAILED REQUEST FOR FACULTIES PAGE")
		
		# Initialize BeautifulSoup
		soup = BeautifulSoup(r.text, features="html.parser")

		# Get all Faculty HTML elements
		items = soup.find_all(class_="item-container")
		for f in items:
			# Get Faculty name data
			name = f.find(class_="generic-title").text.strip()

			if name in facultyMaps:
				name = facultyMaps[name]

			# Check for existing Faculty
			faculty = Faculty.query.filter(Faculty.name.ilike(name)).first()
			prints(2, f"FACULTY: {name}", False)
			if faculty:
				prints(0, f"ALREADY EXISTS (# {faculty.id}), skipping...")
			else: # Create new Faculty
				prints(0, "creating row...")
				faculty = Faculty(name=name)
				db.session.add(faculty)
				db.session.commit()

			# Get all Subject links
			subjects = f.find(class_="generic-body").find_all("a")

			for s in subjects:
				# Get Subject code, skip if too short
				code = s.text.replace(" ", "")
				if len(code) < 3 or len(code) > 6 or not code.isupper():
					continue
				
				# Get Subject sub-url (site)
				url = s["href"]

				prints(4, f"SUBJECT '{code}'", False)

				# Request Subject page
				try:
					r = requests.get(UNI_CAL_URL + version + url, timeout=TIMEOUT)
					if r.status_code != 200:
						raise requests.exceptions.RequestException()
				except requests.exceptions.RequestException:
					# In case normal page does not work, request print page
					try:
						r = requests.get(UNI_CAL_URL + version + "print_" + url, timeout=TIMEOUT)
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
					if subject.faculty_id != faculty.id:
						prints(4, f"- faculty_id does not match: (db) {subject.faculty_id} != {faculty.id}, updating...")
						#subject.faculty_id = faculty.id
					if subject.name != name:
						prints(4, f"- name does not match: (db) {subject.name} != {name}, updating...")
						subject.name = name
					if subject.site != url:
						prints(4, f"- site does not match: (db) {subject.site} != {url}, updating...")
						subject.site = url
					subject.calversion = version
					subject.old = vIndex < len(UNI_CAL_VERSIONS) - 1
				else: # Create new Subject
					prints(0, "creating row...")
					subject = Subject(faculty.id, code, name, url)
					subject.calversion = version
					subject.old = vIndex < len(UNI_CAL_VERSIONS) - 1
					db.session.add(subject)
				db.session.commit()
				
				# Get all Course HTML elements (rows)
				rows = soup.find_all(class_="item-container")

				for c in rows:
					# Skip invalid rows
					if not c.find_all("table"):
						continue
					
					# Get Course number and name data
					try:
						num1, num2, name = [i.text.strip() for i in c.find_all(class_="course-code")]
						number = int((num1 + " " + num2).replace("\r", "").replace("\n", "").split(" ")[-1])
					except:
						continue

					prints(6, f"COURSE '{number}'", False)

					# Get units data
					try:
						units = round(float(c.find(class_="course-hours").text.split(" ")[0]), 2)
					except:
						units = 0

					# Get desc data
					desc = c.find(class_="course-desc")
					if desc:
						desc = desc.text.strip().replace("\n", " ")
					
					# Get prereqs data
					prereqs = c.find(class_="course-prereq")
					if prereqs:
						prereqs = prereqs.text.strip().replace("\n", " ")

					# Get coreqs data
					coreqs = c.find(class_="course-coreq")
					if coreqs:
						coreqs = coreqs.text.strip().replace("\n", " ")

					# Get antireqs data
					antireqs = c.find(class_="course-antireq")
					if antireqs:
						antireqs = antireqs.text.strip().replace("\n", " ")
					
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
							notes = notes + "\n" if notes else ""
							notes += repeatText
					repeat = bool(repeatText)
					
					# Get countgpa data
					nogpaText = c.find(class_="course-nogpa")
					if nogpaText:
						nogpaText = nogpaText.text.strip()
						if nogpaText:
							notes = notes + "\n" if notes else ""
							notes += nogpaText
					countgpa = not bool(nogpaText)

					# Get subsite data
					subsite = None
					link = c.find("a")
					if "name" in link.attrs:
						subsite = link["name"].split("#")[-1]
					elif "href" in link.attrs:
						subsite = link["href"].split("#")[-1]
					
					# Check for existing Course
					course = Course.query.filter_by(subject_id=subject.id, number=number).first()

					if course: # Update Course attributes
						prints(0, f"ALREADY EXISTS (# {course.id}), checking for changed values...")
						if course.subject_id != subject.id:
							prints(6, f"- subject_id does not match: (db) {course.subject_id} != {subject.id}, updating...")
							course.subject_id = subject.id
						if course.units != units:
							prints(6, f"- units does not match: (db) {course.units} != {units}, updating...")
							course.units = units
						if course.name != name:
							prints(6, f"- name does not match: (db) {course.name} != {name}, updating...")
							course.name = name
						if course.desc != desc:
							prints(6, f"- desc does not match: (db) {course.desc} != {desc}, updating...")
							course.desc = desc
						if course.prereqs != prereqs:
							prints(6, f"- prereqs does not match: (db) {course.prereqs} != {prereqs}, updating...")
							course.prereqs = prereqs
						if course.coreqs != coreqs:
							prints(6, f"- coreqs does not match: (db) {course.coreqs} != {coreqs}, updating...")
							course.coreqs = coreqs
						if course.antireqs != antireqs:
							prints(6, f"- antireqs does not match: (db) {course.antireqs} != {antireqs}, updating...")
							course.antireqs = antireqs
						if course.notes != notes:
							prints(6, f"- notes does not match: (db) {course.notes} != {notes}, updating...")
							course.notes = notes
						if course.aka != aka:
							prints(6, f"- aka does not match: (db) {course.aka} != {aka}, updating...")
							course.aka = aka
						if course.repeat != repeat:
							prints(6, f" - repeat does not match: (db) {course.repeat} != {repeat}, updating...")
							course.repeat = repeat
						if course.countgpa != countgpa:
							prints(6, f"- countgpa does not match: (db) {course.countgpa} != {countgpa}, updating...")
							course.countgpa = countgpa
						if course.subsite != subsite:
							prints(6, f"- subsite does not match: (db) {course.subsite} != {subsite}, updating...")
							course.subsite = subsite
						course.calversion = version
						course.old = vIndex < len(UNI_CAL_VERSIONS) - 1
					else: # Create new course
						prints(0, "creating row...")
						course = Course(subject.id, number, name, units)
						course.desc = desc
						course.prereqs = prereqs
						course.coreqs = coreqs
						course.antireqs = antireqs
						course.notes = notes
						course.aka = aka
						course.repeat = repeat
						course.countgpa = countgpa
						course.subsite = subsite
						course.calversion = version
						course.old = vIndex < len(UNI_CAL_VERSIONS) - 1
						db.session.add(course)
					db.session.commit()
