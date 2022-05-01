from app.models import Faculty
from app.routes.views import view

from flask import render_template, flash, redirect
from flask.helpers import url_for


@view.route("/f/<fac>")
def faculty(fac):
	faculty = Faculty.query.filter_by(subdomain=fac).first()
	if not faculty:
		faculty = Faculty.query.get(fac)
		if faculty:
			if faculty.subdomain:
				return redirect(url_for("view.faculty", fac=faculty.subdomain))
		else:
			flash(f"Faculty with id {fac} does not exist!", "danger")
			return redirect(url_for("view.home"))
	return render_template("faculty.html",
		title = faculty.subdomain.capitalize() if faculty.subdomain else faculty.name,
		description = f"Faculty info for {faculty.name}",
		faculty = faculty,
		len = {
			"subjects": len(faculty.subjects),
			"courses": sum([len(s.courses) for s in faculty.subjects]),
			"users": len(faculty.users)
		},
		subjects = [{
			"id": s.id,
			"emoji": s.getEmoji(),
			"code": s.code,
			"name": s.name,
			"url": s.url
		} for s in faculty.subjects],
	)
