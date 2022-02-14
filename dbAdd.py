from planner import db
from planner.models import *
from bs4 import BeautifulSoup

import json, requests

# ADD ROLES

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

# ADD SEASONS

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

# ADD TERMS

termsFile = "backups/terms.json"

with open(termsFile, "r") as file:
	terms = json.load(file)

for tId, term in terms.items():
	try:
		season, year = term.split(" ")
	except:
		print(f"ERROR: term '{term}' is not formatted correctly")
		continue
	try:
		sId = seasons.index(season.lower()) + 1
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

# ADD GRADES

systemWebsite = "https://www.ucalgary.ca/pubs/calendar/current/f-1-1.html"

r = requests.get(systemWebsite)
soup = BeautifulSoup(r.text, features="html.parser")

content = soup.find(id="ctl00_ctl00_pageContent")
table = content.find("tbody")
rows = table.find_all("tr")[1:]

for i, row in enumerate(rows):
	try:
		symbol, gpv, desc = [i.text.strip().split("\n")[0] for i in row.find_all("td")]
		gpv = float(gpv) if gpv else None
	except:
		print(f"ERROR: Could not parse row {i + 1}")
		pass

	g = Grade.query.filter_by(symbol=symbol).first()

	if g:
		print(f"GRADE with symbol '{symbol}' ALREADY EXISTS")
		if g.gpv != gpv:
			print(f"  - gpv does not match: (db) {g.gpv} != {gpv}, updating...")
			g.gpv = gpv
		if g.desc != desc:
			print(f"  - description does not match: (db) {g.desc} != {desc}, updating...")
			g.desc = desc
		db.session.commit()
	else:
		print(f"CREATING GRADE with symbol '{symbol}'")
		g = Grade(symbol, gpv, desc)
		db.session.add(g)
		db.session.commit()