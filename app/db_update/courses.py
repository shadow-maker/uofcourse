from . import _calendars
from app.models import Calendar

def update():
	print("\n" + ("-" * 20) + "UPDATING COURSE DATA" + ("-" * 20))
	print((" " * 20) + "(Calendar, Faculty, Subject, Course)\n")
	_calendars.update(Calendar.query.order_by(Calendar.year).all())
