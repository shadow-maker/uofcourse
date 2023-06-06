from app.models import User, Role
from app.auth import current_user
from app.forms import unameValidation, nameValidation, passwValidation
from app.routes.admin import BaseModelView

from flask import flash
from flask_admin.babel import gettext
from flask_admin.contrib.sqla import form

from wtforms import validators

class UserModelView(BaseModelView):
	def is_accessible(self):
		return current_user.is_authenticated and current_user.role >= Role.admin
	
	column_list = ["id", "username", "role", "name", "email", "created", "units", "faculty_id"]
	column_details_list = [
		"id", "username", "role", "name", "email", "created", "units", "faculty"
	]
	column_filters = ["role", "faculty_id", "faculty"]
	form_excluded_columns = ["created", "logs", "tags", "collections"]

	# Default form args
	form_args = {
		"username": {
			"validators": [validators.DataRequired(), unameValidation]
		},
		"name": {
			"validators": [nameValidation]
		},
		"email": {
			"validators": [validators.DataRequired(), validators.Email()]
		},
		"password": {
			"validators": [validators.DataRequired(), passwValidation]
		},
		"units": {
			"validators": [validators.NumberRange(min=0.0, max=999.99)]
		}
	}
	
	def __init__(self, *args, **kwargs):
		super().__init__(User, *args, **kwargs)
		#self.can_view_details = False
		self.menu_icon_value = "bi-people-fill"
		self.can_export = False

	# Override to exclude password column
	def get_edit_form(self):
		excluded_columns = self.form_excluded_columns + ["password"]

		converter = self.model_form_converter(self.session, self)
		form_class = form.get_form(self.model, converter,
			base_class = self.form_base_class,
			only = self.form_columns,
			exclude = excluded_columns,
			field_args = self.form_args,
			ignore_hidden = self.ignore_hidden,
			extra_fields = self.form_extra_fields
		)

		if self.inline_models:
			form_class = self.scaffold_inline_form_models(form_class)

		return form_class

	# Override to use User.__init__() native constructor
	def create_model(self, form):
		try:
			model = User(
				form.username.data,
				form.name.data,
				form.email.data,
				form.password.data,
				form.faculty.data.id
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

	# Override to use native User.delete() method
	def delete_model(self, model):
		try:
			model.delete()
			self.session.commit()
		except Exception as ex:
			if not self.handle_view_exception(ex):
				flash(gettext("Failed to delete record. %(error)s", error=str(ex)), "error")
			self.session.rollback()
			return False
		else:
			self.after_model_delete(model)

		return True
