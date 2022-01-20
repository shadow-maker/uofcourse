from planner.models import *

from datetime import datetime
from os import path, makedirs
import csv

def backupTables(tables, folder="backups"):
	directory = path.join(folder, datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%H-%M"))

	makedirs(directory, exist_ok=True)

	for table in tables:
		filepath = path.join(directory, f"{table.__tablename__}.csv")
		print(f"Saving {table.__tablename__} table to {filepath}...")
		with open(filepath, "w") as file:
			writer = csv.DictWriter(file, fieldnames=dict(table.query.first()).keys())
			writer.writeheader()
			for row in table.query.all():
				writer.writerow(dict(row))

if __name__ == "__main__":
	backupTables([Faculty, Subject, Course])