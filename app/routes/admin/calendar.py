from app.models import Calendar
from app.routes.admin import BaseModelView

class CalendarModelView(BaseModelView):
	column_default_sort = [("year", True) , ("version", False)]
	form_excluded_columns = ["terms"]
	column_details_list = ["id", "year", "schoolyear", "version", "url"]

	def __init__(self, *args, **kwargs):
		super().__init__(Calendar, *args, **kwargs)
