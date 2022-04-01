from . import TIMEOUT
from planner.constants import UNI_BASE_URL
from planner.models import db, Grade
from bs4 import BeautifulSoup
import requests
import sys

def update():
	url = "f-1-1.html"

	try:
		r = requests.get(UNI_BASE_URL + url, timeout=TIMEOUT)
	except requests.exceptions.RequestException:
		sys.exit(f"FAILED REQUEST FOR GRADE SYSTEM PAGE ({url})")
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
			if (float(g.gpv) if g.gpv else None) != gpv:
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
