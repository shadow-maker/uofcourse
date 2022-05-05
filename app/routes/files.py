from app import app

from flask import Blueprint, send_from_directory

import os

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
