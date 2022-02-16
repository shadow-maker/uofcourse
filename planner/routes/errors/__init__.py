from flask import Blueprint
error = Blueprint("errors", __name__)

from planner.routes.errors.handlers import *