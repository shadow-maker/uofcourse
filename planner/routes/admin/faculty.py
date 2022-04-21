from planner.models import Faculty
from planner.routes.admin import BaseModelView

class FacultyModelView(BaseModelView):
	column_filters = ["name"]
	form_excluded_columns = ["subjects", "users"]

	def __init__(self, *args, **kwargs):
		super().__init__(Faculty, *args, **kwargs)
		self.form_columns
