from app.models import Calendar
from app.routes.admin import BaseModelView

class CalendarModelView(BaseModelView):
	column_list = ["id", "year", "version"]
	column_default_sort = [("year", True) , ("version", False)]
	form_excluded_columns = ["courses", "subjects"]
	column_details_list = ["id", "year", "schoolyear", "version", "grades_page", "faculties_page", "url"]

	def __init__(self, *args, **kwargs):
		super().__init__(Calendar, *args, **kwargs)
		self.menu_icon_value = "bi-calendar-fill"
