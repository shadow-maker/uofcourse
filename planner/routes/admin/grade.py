from planner.models import Grade
from planner.routes.admin import BaseModelView

class GradeModelView(BaseModelView):
	form_excluded_columns = ["userCourses"]

	column_filters = ["gpv", "passed"]

	def __init__(self, *args, **kwargs):
		super().__init__(Grade, *args, **kwargs)
