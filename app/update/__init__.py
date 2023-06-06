#
# SCRIPTS TO UPDATE DATABASE BASED ON UNI DATA
#

from . import terms, grades, courses
from app import app

import click
import sys

@app.cli.command("update", help="Update database with new university data.")
@click.argument("item")
def updateItem(item):
	item = item.lower()
	if item in ["term", "terms"]:
		terms.update()
	elif item in ["grade", "grades"]:
		grades.update()
	elif item in ["course", "courses"]:
		courses.update()
	elif item == "all":
		terms.update()
		grades.update()
		courses.update()
	else:
		sys.exit("Invalid item to update. Available options: terms, grades, courses, all")
