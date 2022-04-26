from app.models import Subject
from app.routes.admin import BaseModelView

from flask import Markup
from flask_admin.model.template import macro

class SubjectModelView(BaseModelView):
	column_list = ["id", "code", "name", "emoji", "faculty_id", "site"]
	column_details_list =["id", "code", "name", "emoji", "faculty", "site", "url", "url_uni"]
	column_filters = ["name", "emoji", "faculty_id", "faculty"]
	form_excluded_columns = ["courses"]

	column_formatters = dict(
		emoji=lambda v, c, m, p: Markup(f"<span>&#{m.emoji}</span>") if m.emoji else ""
	)

	column_formatters_detail = dict(
		emoji=lambda v, c, m, p: Markup(f"&#{m.emoji} (#{m.emoji})") if m.emoji else ""
	)

	def __init__(self, *args, **kwargs):
		super().__init__(Subject, *args, **kwargs)
