#
# SCRIPTS TO UPDATE DATABASE BASED ON UNI DATA
#

TIMEOUT = (5, 30) # Connection timeout, Read timeout

def prints(n, msg, newLine=True):
	print(" " * n + msg, end="\n" if newLine else " ")

from app.models import Course, Grade, Term
from app.db_update import courses, grades, terms


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
		print("\n")
		print(msg + "-" * (80 - len(msg)))
		print("\n")
		updateFuncs[table]()
