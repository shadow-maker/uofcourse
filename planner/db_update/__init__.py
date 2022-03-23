BACKUPS_FOLDER = "backups"

from planner.models import *
from planner.db_update import courses, grades, roles, seasons, terms
from planner.db_update.backup import backup
from planner.db_update.load import load

updateFuncs = {
	Course : courses.update,
	Grade : grades.update,
	Role : roles.update,
	Season : seasons.update,
	Term : terms.update
}


def update(tables=list(updateFuncs.keys()), backupTables=True, backupFolder=BACKUPS_FOLDER):
	for table in tables:
		if table not in updateFuncs.keys():
			continue

		msg = f"UPDATING TABLE {table.__tablename__} "
		print("\n\n")
		print(msg + "-" * (80 - len(msg)))
		print("\n")
		updateFuncs[table]()

		if backupTables:
			msg = f"BACKING UP TABLE {table.__tablename__} "
			print("\n")
			print(msg + "-" * (80 - len(msg)))
			print("\n")
			backup([table], backupFolder)
