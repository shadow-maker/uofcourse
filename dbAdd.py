from planner import db
from planner.models import Role, Season, Term

import json

roles = {
	1 : "user",
	2 : "moderator",
	3 : "admin"
}

for id, name in roles.items():
	role = Role.query.filter_by(id=id).first()
	if role:
		print(f"ROLE {id} ALREADY EXISTS")
		if role.name != name:
			print(f"  - name does not match: (db) {role.name} != {name}, updating...")
			role.name = name
			db.session.commit()
	else:
		print(f"CREATING ROLE {id}")
		role = Role(id=id, name=name)
		db.session.add(role)
		db.session.commit()

termsFile = "backups/terms.json"

seasons = ["winter", "spring", "summer", "fall"]

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

with open(termsFile, "r") as file:
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
