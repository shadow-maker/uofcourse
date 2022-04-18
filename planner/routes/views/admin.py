from planner import app, db
from planner.models import Role, User, UserLog, UserTag, CourseCollection, Grade, Course, Subject, Faculty, Term
from planner.auth import current_user
from planner.forms import unameCheck, unameValidation, unameExists, unameNew, nameValidation, passwValidation
from planner.constants import SITE_NAME

from flask import redirect, flash
from flask.helpers import url_for
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView, form
from flask_admin.form import rules
from flask_admin.babel import gettext

from wtforms import validators

from planner.models.course_collection import CourseCollection


class IndexView(AdminIndexView):
	def is_accessible(self):
		return current_user.is_authenticated and current_user.role >= Role.moderator

	def inaccessible_callback(self, name, **kwargs):
		if current_user.is_authenticated:
			flash(f"You do not have permission to access this page!", "danger")
			return redirect(url_for("view.home"))
		flash(f"You need to log in first!", "warning")
		return redirect(url_for("view.login"))


class BaseModelView(ModelView):
	def is_accessible(self):
		self.can_delete = current_user.role >= Role.admin
		self.can_export = current_user.role >= Role.admin
		return current_user.is_authenticated and current_user.role >= Role.moderator

	def inaccessible_callback(self, name, **kwargs):
		if current_user.is_authenticated:
			flash(f"You do not have permission to access this page!", "danger")
			return redirect(url_for("view.home"))
		flash(f"You need to log in first!", "warning")
		return redirect(url_for("view.login"))

	def __init__(self, model, *args, **kwargs):
		if self.column_list is None and self.column_exclude_list is None:
			self.column_list = [c.name for c in model.__table__.columns]
		#self.column_labels = dict([(c.name, c.name) for c in model.__table__.columns])
		if self.column_sortable_list is None:
			self.column_sortable_list = self.column_list
		if "id" in self.column_list:
			self.column_default_sort = "id"
		self.can_view_details = True
		if self.column_details_list is None:
			self.column_details_list = self.column_list
		super().__init__(model, db.session, *args, **kwargs)


class UserModelView(BaseModelView):
	def is_accessible(self):
		return current_user.is_authenticated and current_user.role >= Role.admin
	
	column_list = ["id", "username", "role", "name", "email", "created", "neededUnits", "faculty_id"]
	column_sortable_list = ["id", "username", "role", "name", "email", "created", "neededUnits"]
	column_details_list = [
		"id", "username", "role", "name", "email", "created", "neededUnits", "faculty"
	]
	form_excluded_columns = ["created", "tags", "collections"]

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
		"neededUnits": {
			"validators": [validators.NumberRange(min=0.0, max=999.99)]
		}
	}
	
	def __init__(self, *args, **kwargs):
		super().__init__(User, *args, **kwargs)
		#self.can_view_details = False
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


class UserLogModelView(BaseModelView):
	def __init__(self, *args, **kwargs):
		super().__init__(UserLog, *args, **kwargs)


class TagModelView(BaseModelView):
	def __init__(self, *args, **kwargs):
		super().__init__(UserTag, *args, **kwargs)


class CollectionModelView(BaseModelView):
	def __init__(self, *args, **kwargs):
		super().__init__(CourseCollection, *args, **kwargs)


class GradeModelView(BaseModelView):
	form_excluded_columns = ["userCourses"]

	def __init__(self, *args, **kwargs):
		super().__init__(Grade, *args, **kwargs)


class FacultyModelView(BaseModelView):
	form_excluded_columns = ["subjects", "users"]

	def __init__(self, *args, **kwargs):
		super().__init__(Faculty, *args, **kwargs)
		self.form_columns


class SubjectModelView(BaseModelView):
	column_list = ["id", "code", "name", "emoji", "faculty_id", "site"]
	column_details_list =["id", "code", "name", "emoji", "faculty", "site", "url", "url_uni"]
	form_excluded_columns = ["courses"]

	#column_formatters = dict(emoji=lambda v, c, m, p: f"&#{m.emoji}")

	def __init__(self, *args, **kwargs):
		super().__init__(Subject, *args, **kwargs)


class CourseModelView(BaseModelView):
	column_list = ["id", "code", "name", "number", "subject_id", "units"]
	column_sortable_list = ["id", "number", "subject_id", "name", "units"]
	column_details_list = [
		"id", "code", "number", "subject", "name", "units", "repeat", "nogpa", "desc", "notes", "prereqs", "coreqs", "antireqs", "url", "url_uni"
	]
	form_excluded_columns = ["userCourses", "userTags"]

	def __init__(self, *args, **kwargs):
		super().__init__(Course, *args, **kwargs)


class TermModelView(BaseModelView):
	form_excluded_columns = ["courseCollections"]

	def __init__(self, *args, **kwargs):
		super().__init__(Term, *args, **kwargs)


admin = Admin(app, name=f"{SITE_NAME} Admin", template_mode="bootstrap4", base_template="admin/master.html", index_view=IndexView())

admin.add_views(
	UserModelView(),
	UserLogModelView(),
	TagModelView(),
	CollectionModelView(),
	GradeModelView(),
	FacultyModelView(),
	SubjectModelView(),
	CourseModelView(),
	TermModelView()
)
