from app.models.utils import getSubjectByCode
from app.routes.views import view

from flask import render_template, flash, redirect
from flask.helpers import url_for

@view.route("/s/<subjectCode>")
def subject(subjectCode):
	if not subjectCode.isupper():
		return redirect(url_for("view.subject",	subjectCode=subjectCode.upper()))
	subject = getSubjectByCode(subjectCode)
	if not subject:
		flash(f"Subject with code {subjectCode} does not exist!", "danger")
		return redirect(url_for("view.home"))
	faculty = subject.faculty
	return render_template("subject.html",
		title = subjectCode.upper(),
		description = f"Subject info for {subject.code} : {subject.name}",
		subject = subject,
		faculty = faculty,
		lenCourses = len(subject.courses)
	)
