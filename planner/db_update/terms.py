from . import BACKUPS_FOLDER
from planner.models import db, Season, Term
import os
import json

def update():
	termsFile = os.path.join(BACKUPS_FOLDER, "terms.json")

	with open(termsFile, "r") as file:
		terms = json.load(file)

	for tId, term in terms.items():
		try:
			season, year = term.split(" ")
		except:
			print(f"ERROR: term '{term}' is not formatted correctly")
			continue
		try:
			sId = Season.query.filter_by(name=season.lower()).first().id
		except:
			print(f"ERROR: Season '{season}' not found")
			continue
		try:
			year = int(year)
		except:
			print(f"ERROR: Year '{year}' cannot be casted to int")
			continue

		t = Term.query.filter_by(id=tId).first()
		if t:
			print(f"TERM {tId} ALREADY EXISTS")
			if t.season_id != sId:
				print(f"  - seasonId does not match: (db) {t.season_id} != {sId}, updating...")
				t.season_id = sId
			if t.year != year:
				print(f"  - year does not match: (db) {t.year} != {year}, updating...")
				t.year = year
			db.session.commit()
		else:
			print(f"CREATING TERM {tId}")
			t = Term(id=tId, season_id=sId, year=year)
			db.session.add(t)
			db.session.commit()
