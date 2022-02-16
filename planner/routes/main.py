from planner.models import User
from planner.queryUtils import *
from planner.constants import *

from flask import Blueprint, render_template

main = Blueprint("main", __name__)

#
# Routes
#

@main.route("/home")
@main.route("/")
def viewHome():
	return render_template("index.html", header="UofC Planner")


@main.route("/about")
def viewAbout():
	return render_template("about.html", title="About", header="About UofC Planner")
