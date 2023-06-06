from app.models import UserLog, Role
from app.auth import current_user
from app.routes.admin import BaseModelView

class UserLogModelView(BaseModelView):
	def is_accessible(self):
		return current_user.is_authenticated and current_user.role >= Role.admin
	
	can_create = False
	can_edit = False
	can_delete = False

	column_filters = ["user_id", "event"]
	column_default_sort = ("datetime", True)
	column_details_list = ["id", "user", "event", "datetime", "ip", "location"]

	def locationFormat(v, c, m, p):
		l = m.location
		if l["status"] == "success":
			return f"{l['isp']} - {l['city']}, {l['region']}, {l['countryCode']} ({l['lat']}, {l['lon']})"
		else:
			return f"ERROR: {l['message']}"


	column_formatters = dict(location=locationFormat)

	def __init__(self, *args, **kwargs):
		super().__init__(UserLog, *args, **kwargs)
		self.menu_icon_value = "bi-person-fill-check"
