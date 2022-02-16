from planner.queryUtils import *
from planner.constants import *

from planner.routes.views import view

from flask import render_template


@view.route("/home")
@view.route("/")
def viewHome():
	return render_template("index.html", header="UofC Planner")


@view.route("/about")
def viewAbout():
	return render_template("about.html", title="About", header="About UofC Planner")
