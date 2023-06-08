from app.models import Faculty
from app.routes.admin import BaseModelView

class FacultyModelView(BaseModelView):
	column_filters = ["name"]
	form_excluded_columns = ["subjects", "users"]

	def __init__(self, *args, **kwargs):
		super().__init__(Faculty, *args, **kwargs)
		self.menu_icon_value = "bi-bank"
