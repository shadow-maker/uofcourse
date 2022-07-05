from app import db
from app.models import Role, Season, Term, Grade
from app.auth import current_user, login_required
from app.forms import formChangePassw
from app.constants import *

from app.routes.views import view
from app.routes.api.me import *

from flask import render_template, flash, session


@view.route("/account", methods=["GET", "POST"])
@login_required
def account():
	formPassw = formChangePassw()

	if formPassw.validate_on_submit():
		if current_user.checkPassw(formPassw.oldPassw.data):
			try:
				current_user.updatePassw(formPassw.newPassw.data)
				db.session.commit()
			except:
				db.session.rollback()
				flash(f"Error updating password!", "danger")
			else:
				flash(f"Password changed!", "success")
		else:
			flash(f"Current password is incorrect! - Password not changed", "danger")
	
	return render_template("account.html",
		title = "Account",
		header = "My Acccount",
		headerIcon = "person-circle",
		formPassw = formPassw
	)


@view.route("/tags")
@login_required
def tags():
	return render_template("tags.html",
		title = "My Tags",
		header = "My Tags",
		tags = current_user.tags
	)

@view.route("/planner")
@login_required
def planner():
	return render_template("planner.html",
		title = "My Plan",
		header = "My Course Plan",
		headerIcon = "calendar-range",
		transferred = "transferred" in session and session["transferred"],
		grades = {grade.id : dict(grade) for grade in Grade.query.all()},
		seasons = list(Season),
		years = sorted(set([t[0] for t in Term.query.with_entities(Term.year)]), reverse=True),
		summaryXYOptions = ["subjects", "faculties", "levels", "grades", "terms"],
		summaryShowOptions = ["courses", "units"],
		selCollectionCourse = request.args.get("id"),
	)
