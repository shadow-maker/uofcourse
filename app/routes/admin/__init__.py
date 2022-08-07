from app import app, db, ipcache
from app.models import Role
from app.auth import current_user
from app.constants import SITE_NAME

from flask import redirect, flash
from flask.helpers import url_for
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView

from sys import getsizeof


class IndexView(AdminIndexView):
	def is_accessible(self):
		return current_user.is_authenticated and current_user.role >= Role.moderator

	def inaccessible_callback(self, name, **kwargs):
		if current_user.is_authenticated:
			flash(f"You do not have permission to access this page!", "danger")
			return redirect(url_for("view.home"))
		flash(f"You need to log in first!", "warning")
		return redirect(url_for("view.login"))

	@expose("/")
	def index(self):
		return self.render("admin/index.html", len=len, getsizeof=getsizeof, ipcache=ipcache)


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
		if self.column_default_sort is None and "id" in self.column_list:
			self.column_default_sort = "id"
		self.can_view_details = True
		if self.column_details_list is None:
			self.column_details_list = self.column_list
		super().__init__(model, db.session, *args, **kwargs)


admin = Admin(app,
	url = "/admin",
	name = SITE_NAME,
	template_mode = "bootstrap4",
	base_template = "admin/master.html",
	index_view = IndexView()
)

from app.routes.admin.user import UserModelView
from app.routes.admin.user_log import UserLogModelView
from app.routes.admin.announcement import AnnouncementModelView
from app.routes.admin.features import FeatureRequestModelView
from app.routes.admin.grade import GradeModelView
from app.routes.admin.faculty import FacultyModelView
from app.routes.admin.subject import SubjectModelView
from app.routes.admin.course import CourseModelView
from app.routes.admin.calendar import CalendarModelView
from app.routes.admin.term import TermModelView

admin.add_views(
	UserModelView(),
	UserLogModelView(),
	AnnouncementModelView(),
	FeatureRequestModelView(),
	GradeModelView(),
	FacultyModelView(),
	SubjectModelView(),
	CourseModelView(),
	CalendarModelView(),
	TermModelView()
)
