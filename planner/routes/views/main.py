from planner import changelog as change

from planner.queryUtils import *
from planner.constants import *

from planner.routes.views import view

from flask import render_template


@view.route("/home")
@view.route("/")
def home():
	return render_template("index.html", header="UofC Planner")


@view.route("/about")
def about():
	return render_template("about.html", title="About", header="About UofC Planner")


@view.route("/changelog")
def changelog():
	return render_template("changelog.html",
		title="Changelog",
		header="Changelog",
		changelog = change
	)
