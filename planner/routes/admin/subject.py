from planner.models import Subject
from planner.routes.admin import BaseModelView

class SubjectModelView(BaseModelView):
	column_list = ["id", "code", "name", "emoji", "faculty_id", "site"]
	column_details_list =["id", "code", "name", "emoji", "faculty", "site", "url", "url_uni"]
	column_filters = ["name", "emoji", "faculty_id", "faculty"]
	form_excluded_columns = ["courses"]

	#column_formatters = dict(emoji=lambda v, c, m, p: f"&#{m.emoji}")

	def __init__(self, *args, **kwargs):
		super().__init__(Subject, *args, **kwargs)
