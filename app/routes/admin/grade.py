from app.models import Grade
from app.routes.admin import BaseModelView

class GradeModelView(BaseModelView):
	form_excluded_columns = ["collectionCourses"]

	column_filters = ["gpv", "passed"]

	def __init__(self, *args, **kwargs):
		super().__init__(Grade, *args, **kwargs)
