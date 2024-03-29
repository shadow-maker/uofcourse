from app import db
from app.models import Season, Term
import json
import os

def update():
	termsFile = "terms.json"
	termsPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), termsFile)

	with open(termsPath, "r") as file:
		terms = json.load(file)

	for tId, term in terms.items():
		try:
			season = term["season"]
			year = term["year"]
		except:
			print(f"ERROR: term '{term}' is not formatted correctly")
			continue

		try:
			s = getattr(Season, season)
		except:
			print(f"ERROR: Season '{season}' not found")
			continue

		try:
			year = int(year)
		except:
			print(f"ERROR: Year '{year}' cannot be casted to int")
			continue

		t = Term.query.get(tId)
		if t:
			print(f"TERM {tId} ALREADY EXISTS")
			if t.season != s:
				print(f"  - season does not match: (db) {t.season} != {s}, updating...")
				t.season = s
			if t.year != year:
				print(f"  - year does not match: (db) {t.year} != {year}, updating...")
				t.year = year
			db.session.commit()
		else:
			print(f"CREATING TERM {tId}")
			t = Term(id=tId, season=season, year=year)
			db.session.add(t)
			db.session.commit()
