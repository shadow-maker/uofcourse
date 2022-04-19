from planner.models import Term
from planner.routes.admin import BaseModelView

class TermModelView(BaseModelView):
	column_filters = ["season", "year", "start", "end"]
	column_default_sort = ("year", True)
	form_excluded_columns = ["courseCollections"]

	def __init__(self, *args, **kwargs):
		super().__init__(Term, *args, **kwargs)
