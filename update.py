from sys import argv
from app.db_update import updateFuncs, update

if __name__ == "__main__":
	def findTable(name):
		for table in updateFuncs.keys():
			if table.__tablename__ == name:
				return table
		return None

	tables = []
	if len(argv) > 1:
		if argv[1].lower() == "all":
			tables = list(updateFuncs.keys())
		else:
			for arg in argv[1:]:
				table = findTable(arg)
				if table:
					tables.append(table)
				else:
					print(f"ERROR: table '{arg}' not found")

	update(tables)
