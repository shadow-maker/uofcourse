from app.models import Announcement, Role
from app.auth import current_user
from app.routes.admin import BaseModelView

from flask import flash
from flask_admin.babel import gettext

class AnnouncementModelView(BaseModelView):
	def is_accessible(self):
		return current_user.is_authenticated and current_user.role >= Role.admin
	
	column_list = ["id", "datetime", "title", "user_id"]
	column_details_list = ["id", "datetime", "user_id", "title", "body"]
	form_excluded_columns = ["read_by", "author", "datetime"]
	column_default_sort = [("datetime", True) , ("title", True)]

	def __init__(self, *args, **kwargs):
		super().__init__(Announcement, *args, **kwargs)
		self.menu_icon_value = "bi-bell-fill"
	
	# Override to use Announcement.__init__() native constructor
	def create_model(self, form):
		try:
			model = Announcement(
				current_user.id,
				form.title.data,
				form.body.data,
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
