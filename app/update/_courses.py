from . import prints
from app.models import db, Calendar, Course

from bs4 import ResultSet

def update(calendar: Calendar, subjectID: int, items: ResultSet):
	for c in items:
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
		course = Course.query.filter_by(subject_id=subjectID, number=number).first()

		if course: # Update Course attributes
			prints(0, f"ALREADY EXISTS (# {course.id}), checking for changed values...")
			if course.subject_id != subjectID:
				prints(6, f"- subject_id does not match: (db) {course.subject_id} != {subjectID}, updating...")
				course.subject_id = subjectID
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
			if calendar not in course.calendars:
				course.calendars.append(calendar)
			course.old =  calendar.version != "current/"
		else: # Create new course
			prints(0, "creating row...")
			course = Course(subjectID, number, name, units)
			course.desc = desc
			course.prereqs = prereqs
			course.coreqs = coreqs
			course.antireqs = antireqs
			course.notes = notes
			course.aka = aka
			course.repeat = repeat
			course.countgpa = countgpa
			course.subsite = subsite
			course.calendars.append(calendar)
			course.old =  calendar.version != "current/"
			db.session.add(course)
		db.session.commit()
