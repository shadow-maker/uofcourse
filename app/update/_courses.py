from ._logger import logger
from app.models import db, Calendar, Course

from bs4 import ResultSet

def update(calendar: Calendar, subjectID: int, items: ResultSet):
	logger.info(f"Found {len(items)} Course items")
	for i, c in enumerate(items):
		# Skip invalid rows
		if not c.find_all("table"):
			logger.debug(f"Course item {i} is invalid (skipping)")
			continue
		
		# Get Course number and name data
		try:
			num1, num2, name = [i.text.strip() for i in c.find_all(class_="course-code")]
			number = int((num1 + " " + num2).replace("\r", "").replace("\n", "").split(" ")[-1])
		except Exception as e:
			logger.warning(f"Course number {i} is invalid (skipping):\n{e}")
			continue

		logger.debug(f"Reading Course with number '{number}'")

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

		if course is not None: # Update Course attributes
			newerVersion = False
			for cal in course.calendars:
				if cal.year > calendar.year:
					newerVersion = True
					break
			if calendar not in course.calendars:
				course.calendars.append(calendar)

			if newerVersion:
				logger.debug(f"Course '{course.code}' (id {course.id}) has a newer version (skipping changes)")
			else:
				logger.debug(f"Course '{course.code}' (id {course.id}) already exists, checking for changed values")
				if course.subject_id != subjectID:
					logger.debug(f"Course subject_id does not match (db) {course.subject_id} != {subjectID} (updating)")
					course.subject_id = subjectID
				if course.units != units:
					logger.debug(f"Course units does not match (db) {course.units} != {units} (updating)")
					course.units = units
				if course.name != name:
					logger.debug(f"Course name does not match (db) {course.name} != {name} (updating)")
					course.name = name
				if course.desc != desc:
					logger.debug(f"Course desc does not match (db) {course.desc} != {desc} (updating)")
					course.desc = desc
				if course.prereqs != prereqs:
					logger.debug(f"Course prereqs does not match (db) {course.prereqs} != {prereqs} (updating)")
					course.prereqs = prereqs
				if course.coreqs != coreqs:
					logger.debug(f"Course coreqs does not match (db) {course.coreqs} != {coreqs} (updating)")
					course.coreqs = coreqs
				if course.antireqs != antireqs:
					logger.debug(f"Course antireqs does not match (db) {course.antireqs} != {antireqs} (updating)")
					course.antireqs = antireqs
				if course.notes != notes:
					logger.debug(f"Course notes does not match (db) {course.notes} != {notes} (updating)")
					course.notes = notes
				if course.aka != aka:
					logger.debug(f"Course aka does not match (db) {course.aka} != {aka} (updating)")
					course.aka = aka
				if course.repeat != repeat:
					logger.debug(f"Course repeat does not match (db) {course.repeat} != {repeat} (updating)")
					course.repeat = repeat
				if course.countgpa != countgpa:
					logger.debug(f"Course countgpa does not match (db) {course.countgpa} != {countgpa} (updating)")
					course.countgpa = countgpa
				if course.subsite != subsite:
					logger.debug(f"Course subsite does not match (db) {course.subsite} != {subsite} (updating)")
					course.subsite = subsite
				course.old =  calendar.version != "current/"
				if course.old:
					logger.debug("Course is not current")
		else: # Create new course
			logger.debug(f"Course '{number}' does not exist (creating)")
			try:
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
			except Exception as e:
				logger.error(f"Failed to create Course '{number}':\n{e}")
			if course.old:
				logger.debug("Course is not current")
		try:
			db.session.commit()
		except Exception as e:
			logger.error(f"Failed to commit Course '{number}':\n{e}")
