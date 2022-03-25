from . import BASE_URL, TIMEOUT
from planner.models import db, Faculty, Subject, Course

from bs4 import BeautifulSoup
import requests
import sys

def update():
	facURL = "course-by-faculty.html"

	try:
		r = requests.get(BASE_URL + facURL, timeout=TIMEOUT)
	except:
		sys.exit(f"FAILED REQUEST FOR FACULTIES PAGE ({url})")
	soup = BeautifulSoup(r.text, features="html.parser")

	content = soup.find(id="ctl00_ctl00_pageContent")
	rows = content.find_all("tr", recursive=False)

	for fac in rows:
		facName = fac.find(class_="generic-title").text.strip()
		body = fac.find(class_="generic-body")
		subjects = {c.text.replace(" ", "") : c["href"] for c in body.find_all("a") if len(c.text.replace(" ", "")) > 2}

		faculty = Faculty.query.filter_by(name=facName).first()
		print(f"FACULTY '{facName}'", end=" ")

		if faculty:
			print(f"ALREADY EXISTS (# {faculty.id}), skipping...")
		else:
			print("creating row...")
			faculty = Faculty(name=facName)
			db.session.add(faculty)
			db.session.commit()

		for subjCode, url in subjects.items():
			print(f"  SUBJECT '{subjCode}'", end=" ")

			try:
				r = requests.get(BASE_URL + url, timeout=TIMEOUT)
			except:
				print("REQUEST FAILED")
				continue

			soup = BeautifulSoup(r.text, features="html.parser")

			content = soup.find(id="ctl00_ctl00_pageContent")

			if content == None:
				print()
				continue

			courses = [c for c in content.find_all("tr", recursive=False) if len(c.find_all("table")) > 0]
			
			subjName = " ".join(soup.find(class_="page-title").text.strip().split(" ")[:-1])

			subject = Subject.query.filter_by(code=subjCode).first()

			if subject:
				print(f"ALREADY EXISTS (# {subject.id}), checking for changed values...")
				if subject.faculty_id != faculty.id:
					print(f"  - facId does not match: (db) {subject.faculty_id} != {faculty.id}, updating...")
					subject.faculty_id = faculty.id
				if subject.name != subjName:
					print(f"  - name does not match: (db) {subject.name} != {subjName}, updating...")
					subject.name = subjName
				if subject.site != url:
					print(f"  - site does not match: (db) {subject.site} != {url}, updating...")
					subject.site = url
			else:
				print("creating row...")
				subject = Subject(faculty_id=faculty.id, code=subjCode, name=subjName, site=url)
				db.session.add(subject)
			db.session.commit()
			
			for c in courses:
				subjName, courseCode, courseName = [i.text for i in c.find_all(class_="course-code")]
				code = int(courseCode.replace(" ", ""))
				name = courseName.strip()

				try:
					units = round(float(c.find(class_="course-hours").text.split(" ")[0]), 2)
				except:
					units = 0
				
				desc = c.find(class_="course-desc").text.strip()
				
				prereqs = c.find(class_="course-prereq")
				if prereqs:
					prereqs = prereqs.text.strip()
		
				antireqs = c.find(class_="course-antireq")
				if antireqs:
					antireqs = antireqs.text.strip()
				
				notes = c.find(class_="course-notes")
				if notes:
					notes = notes.text.strip()

				print(f"    COURSE '{code}'", end=" ")
				
				course = Course.query.filter_by(subject_id=subject.id).filter_by(code=code).first()

				if course:
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
					if course.antireqs != antireqs:
						print(f"    - antireqs does not match: (db) {course.antireqs} != {antireqs}, updating...")
						course.antireqs = antireqs
					if course.notes != notes:
						print(f"    - notes does not match: (db) {course.notes} != {notes}, updating...")
						course.notes = notes
				else:
					print("creating row...")
					course = Course(subject.id, code, name, units, desc, prereqs, antireqs)	
					db.session.add(course)
				db.session.commit()
