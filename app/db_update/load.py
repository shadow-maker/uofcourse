from . import BACKUPS_FOLDER
from app.models import *

import csv
import os

def load(subdir, tables):

	def changeValuesToInt(dictionary):
		for key in dictionary:
			try:
				newVal = int(dictionary[key])
			except:
				continue
			dictionary[key] = newVal
		return dictionary

	files = [f.name for f in os.scandir(os.path.join(BACKUPS_FOLDER, subdir)) if f.is_file() and ".csv" in f.name]

	for table in tables:
		file = [f for f in files if os.path.splitext(f)[0] == table.__tablename__][0]

		if not file:
			continue

		path = os.path.join(BACKUPS_FOLDER, subdir, file)

		with open(path, "r") as file:
			reader = csv.DictReader(file)
			for row in reader:
				row = changeValuesToInt(row)
				instance = table.query.filter_by(id=row["id"]).first()
				if instance:
					print(f"{table.__tablename__} {row['id']} ALREADY EXISTS, skipping...")
					continue
				id = row["id"]
				row.pop("id")
				print(f"CREATING {table.__tablename__} {id}")
				instance = table(**row)
				instance.id = id
				db.session.add(instance)
				db.session.commit()
