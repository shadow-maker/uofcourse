from app import app, jinja

from flask import Blueprint, Response, send_from_directory
from flask.helpers import url_for

import os
import re

#
# Create file route blueprint with no url prefix
#

file = Blueprint("file", __name__, url_prefix="/")

#
# File routes
#

@file.route("/favicon.ico")
def favicon():
	return send_from_directory(app.static_folder, "favicon.ico")


@file.route("/ads.txt")
def ads():
	return send_from_directory(app.static_folder, "ads.txt")


@file.route("/api.md")
def api():
	# Create jinja2 template from api docs markdown file
	with open(os.path.join(app.static_folder, "api.md"), "r", encoding="utf-8") as file:
		template = jinja.from_string(file.read())

	# Process template with variables
	processed = template.render(
		url_for = url_for
	)
	
	# Remove all ids and classes
	processed = re.sub(r"{:(.*?)}", "", processed)

	return Response(processed, mimetype="text/markdown")
