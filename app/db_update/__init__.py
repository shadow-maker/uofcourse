#
# SCRIPTS TO UPDATE DATABASE BASED ON CONSTANT OR UNI DATA
#

BACKUPS_FOLDER = "backups"
TIMEOUT = (5, 30) # Connection timeout, Read timeout

from app.models import Course, Grade, Term

from app.db_update import courses, grades, terms
from app.db_update.backup import backup
from app.db_update.load import load


updateFuncs = {
	Course : courses.update,
	Grade : grades.update,
	Term : terms.update
}


def update(tables=list(updateFuncs.keys())):
	for table in tables:
		if table not in updateFuncs.keys():
			continue

		msg = f"UPDATING TABLE {table.__tablename__} "
		print("\n\n")
		print(msg + "-" * (80 - len(msg)))
		print("\n")
		updateFuncs[table]()
