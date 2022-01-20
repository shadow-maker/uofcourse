from planner import db
from planner.models import Season, Term

import json

seasons = ["Winter", "Spring", "Summer", "Fall"]

for i in range(len(seasons)):
	sId = i + 1
	s = Season.query.filter_by(id=sId).first()
	if s:
		print(f"SEASON {sId} ALREADY EXISTS")
		if s.name != seasons[i]:
			print(f"  - name does not match: (db) {s.name} != {seasons[i]}, updating...")
			s.name = seasons[i]
			db.session.commit()
	else:
		print(f"CREATING SEASON {sId}")
		s = Season(id=sId, name=seasons[i])
		db.session.add(s)
		db.session.commit()

with open("terms.json", "r") as file:
	terms = json.load(file)

for tId, term in terms.items():
	try:
		season, year = term.split(" ")
	except:
		print(f"ERROR: term '{term}' is not formatted correctly")
		continue
	try:
		sId = seasons.index(season) + 1
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
