from ._logger import logger
from app.models import db, Season, Term

import json
import os
import sys

TERMS_FILE = "terms.json"

def update():
	print("\n" + ("-" * 20) + "UPDATING TERMS" + ("-" * 20) + "\n")

	logger.info("Updating TERM table")

	try:
		termsPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), TERMS_FILE)
		with open(termsPath, "r") as file:
			terms = json.load(file)
	except:
		logger.error(f"Could not open terms file '{TERMS_FILE}'")
		sys.exit(f"ERROR: Could not open terms file '{TERMS_FILE}'")

	logger.debug(f"Found {len(terms)} terms")

	for tId, term in terms.items():
		logger.debug(f"Parsing term {tId}")
		try:
			season = term["season"]
			year = term["year"]
		except KeyError as e:
			logger.warning(f"Term '{term}' is not formatted correctly (skipping):\n{e}")
			continue

		try:
			s = getattr(Season, season)
		except AttributeError as e:
			logger.warning(f"Season '{season}' not found (skipping):\n{e}")
			continue

		try:
			year = int(year)
		except ValueError as e:
			logger.warning(f"Year '{year}' cannot be casted to int (skipping):\n{e}")
			continue

		term = Term.query.get(tId)
		if term is not None:
			logger.debug(f"Term {tId} already exists")
			if term.season != s:
				logger.debug(f"Term {tId} season does not match: (db) {term.season} != {s} (updating)")
				term.season = s
			if term.year != year:
				logger.debug(f"Term {tId} year does not match: (db) {term.year} != {year} (updating)")
				term.year = year
		else:
			logger.debug(f"Creating term {tId}")
			try:
				term = Term(id=tId, season=season, year=year)
				db.session.add(term)
			except Exception as e:
				logger.error(f"Could not create term {tId}:\n{e}")
		try:
			db.session.commit()
		except Exception as e:
			logger.error(f"Could not commit term {tId}:\n{e}")
	logger.info("Finished updating TERM table")
