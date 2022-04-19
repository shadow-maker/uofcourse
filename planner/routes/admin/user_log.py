from planner.models import UserLog, Role
from planner.auth import current_user
from planner.routes.admin import BaseModelView

class UserLogModelView(BaseModelView):
	def is_accessible(self):
		return current_user.is_authenticated and current_user.role >= Role.admin
	
	can_create = False
	can_edit = False
	can_delete = False

	column_filters = ["user_id", "event"]
	column_default_sort = ("datetime", True)
	column_details_list = ["id", "user_id", "event", "datetime", "ip", "location"]

	def __init__(self, *args, **kwargs):
		super().__init__(UserLog, *args, **kwargs)
