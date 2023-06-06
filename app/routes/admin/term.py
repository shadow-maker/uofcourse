from app.models import Term
from app.routes.admin import BaseModelView

class TermModelView(BaseModelView):
	column_list = ["id", "season", "year", "start", "end"]
	column_filters = ["season", "year", "start", "end"]
	column_default_sort = [("year", True) , ("season", True)]
	form_excluded_columns = ["collections"]

	def __init__(self, *args, **kwargs):
		super().__init__(Term, *args, **kwargs)
		self.menu_icon_value = "bi-calendar-range-fill"
