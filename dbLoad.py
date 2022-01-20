from planner.models import *

tables = [Course, Faculty, Subject]

import csv
import os
import sys

backupsDir = "backups"
subDir = ""

def getTable(tablename):
	for table in tables:
		if table.__tablename__ == tablename:
			return table


if len(sys.argv) < 2:
	sys.exit("ERROR: No arguments provided")

subDir = sys.argv[1]

files = [f.name for f in os.scandir(os.path.join(backupsDir, subDir)) if f.is_file() and ".csv" in f.name]

for file in files:
	table = getTable(os.path.splitext(file)[0])
	path = os.path.join(backupsDir, subDir, file)

	with open(path, "r") as file:
		reader = csv.DictReader(file)
		for row in reader:
			instance = table.query.filter_by(id=row["id"]).first()
			if instance:
				print(f"{table.__tablename__} {row['id']} ALREADY EXISTS, skipping...")
				continue
			instance = table(**row)
			db.session.add(instance)
			db.session.commit()
