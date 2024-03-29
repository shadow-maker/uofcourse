from app.models import Course
from app.routes.admin import BaseModelView

class CourseModelView(BaseModelView):
	column_list = ["id", "code", "name", "number", "subject_id", "units"]
	column_sortable_list = ["id", "number", "subject_id", "name", "units"]
	column_details_list = [
		"id", "code", "number", "subject", "name", "units", "repeat", "countgpa", "desc", "notes", "prereqs", "coreqs", "antireqs", "url", "url_uni"
	]
	column_filters = ["number", "name", "units", "subject_id", "subject"]
	form_excluded_columns = ["collectionCourses", "tags"]

	def __init__(self, *args, **kwargs):
		super().__init__(Course, *args, **kwargs)
