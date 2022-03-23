from planner import changelog as change

from planner.queryUtils import *
from planner.constants import *

from planner.routes import constants
from planner.routes.views import view

from flask import render_template


@view.route("/home")
@view.route("/")
def home():
	return render_template("index.html",
		constants = constants,
		header="UofC Course Planner"
	)


@view.route("/about")
def about():
	return render_template("about.html",
		constants = constants,
		title="About",
		header="About UofCourse"
	)


@view.route("/changelog")
def changelog():
	return render_template("changelog.html",
		constants = constants,
		title="Changelog",
		header="Changelog",
		changelog = change
	)


@view.route("/api")
def api():
	return render_template("api.html",
		constants = constants,
		title="API",
		header="Coming soon..."
	)
