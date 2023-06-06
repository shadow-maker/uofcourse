#
# SCRIPTS TO UPDATE DATABASE BASED ON UNI DATA
#

from app import app
from app.localdt import utc
from app.logging import LOG_DIR, setLogFileHandler

import click
import logging
import os


logPreFname = os.path.join(os.getcwd(), LOG_DIR, "update-" + utc.now().strftime("%Y-%m-%d"))
logFname = logPreFname + ".log"
count = 1
while os.path.exists(logFname):
	count += 1
	logFname = f"{logPreFname}({count}).log"

logger = logging.getLogger(__name__)

setLogFileHandler(logger, logFname)


from . import terms, grades, courses

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
		logger.error("Invalid item to update. Available options: terms, grades, courses, all")
