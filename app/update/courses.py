from . import _calendars, logger
from app.models import Calendar

def update():
	print("\n" + ("-" * 20) + "UPDATING COURSE DATA" + ("-" * 20))
	logger.info("Updating course data (Calendar, Faculty, Subject, Course)")

	_calendars.update(Calendar.query.order_by(Calendar.year.desc()).all())

	logger.info("Finished updating course data (Calendar, Faculty, Subject, Course)")
