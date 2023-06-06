from ._logger import logger
from ._calendars import update as calendarsUpdate
from app.models import Calendar

def update():
	print("\n" + ("-" * 20) + "UPDATING COURSE DATA" + ("-" * 20))
	logger.info("Updating course data (Calendar, Faculty, Subject, Course)")

	calendarsUpdate(Calendar.query.order_by(Calendar.year.desc()).all())

	logger.info("Finished updating course data (Calendar, Faculty, Subject, Course)")
