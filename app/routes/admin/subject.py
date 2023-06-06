from app.models import Subject
from app.routes.admin import BaseModelView

from flask import Markup, flash
from flask_admin.babel import gettext
from wtforms import validators, StringField


def emojiValidation(form, field):
	if field.data and not (field.data.isdigit() or len(field.data) == 1):
		raise validators.ValidationError("Invalid value for emoji, must be numeric or single character")


class SubjectModelView(BaseModelView):
	column_list = ["id", "code", "name", "emoji", "faculty_id", "site", "old"]
	form_columns = ["code", "name", "faculty", "emoji", "site"]
	column_details_list =["id", "code", "name", "faculty", "emoji", "site", "url", "url_uni", "old"]
	column_filters = ["name", "emoji", "faculty_id", "faculty", "old"]

	form_extra_fields = {
    	"emoji": StringField("Emoji", [emojiValidation])
    }

	column_formatters = dict(
		emoji=lambda v, c, m, p: Markup(f"<span>&#{m.emoji}</span>") if m.emoji else ""
	)

	column_formatters_detail = dict(
		emoji=lambda v, c, m, p: Markup(f"&#{m.emoji} (#{m.emoji})") if m.emoji else ""
	)

	# Override to use custom setEmoji method
	def update_model(self, form, model):
		try:
			emoji = form.emoji.data
			form.emoji = None
			form.populate_obj(model)
			model.setEmoji(emoji)
			self._on_model_change(form, model, False)
			self.session.commit()
		except Exception as ex:
			if not self.handle_view_exception(ex):
				flash(gettext("Failed to update record. %(error)s", error=str(ex)), "error")
			self.session.rollback()
			return False
		else:
			self.after_model_change(form, model, False)
		return True
	
	# Override to use Subject.__init__() native constructor
	def create_model(self, form):
		try:
			model = Subject(
				form.faculty.data.id,
				form.code.data,
				form.name.data,
				form.site.data,
				form.emoji.data
			)
			self.session.add(model)
			self._on_model_change(form, model, True)
			self.session.commit()
		except Exception as ex:
			if not self.handle_view_exception(ex):
				flash(gettext("Failed to create record. %(error)s", error=str(ex)), "error")
			self.session.rollback()
			return False
		else:
			self.after_model_change(form, model, True)
		return model

	def __init__(self, *args, **kwargs):
		super().__init__(Subject, *args, **kwargs)
		self.menu_icon_value = "bi-journals"
