from app.models import FeatureRequest, Role
from app.auth import current_user
from app.routes.admin import BaseModelView

from flask import flash
from flask_admin.babel import gettext

from app.models import Calendar
from app.routes.admin import BaseModelView

class FeatureRequestModelView(BaseModelView):
	def is_accessible(self):
		return current_user.is_authenticated and current_user.role >= Role.admin
	
	column_list = ["id", "datetime", "title", "user_id", "num_likes"]
	column_details_list = ["id", "datetime", "user_id", "title", "body"]
	form_excluded_columns = ["posted_by", "num_likes", "author", "datetime"]
	column_default_sort = [("datetime", True) , ("title", True)]

	def __init__(self, *args, **kwargs):
		super().__init__(FeatureRequest, *args, **kwargs)
	
	# Override to use Announcement.__init__() native constructor
	def create_model(self, form):
		try:
			model = FeatureRequest(
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