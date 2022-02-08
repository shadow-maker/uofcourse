from planner import utcoffset
from planner.models import Term, Faculty, Subject, Course, User

from datetime import datetime, date, time, timedelta

def getById(table, id):
	return table.query.filter_by(id=id).first()

def getAllTerms(asc=True):
	results = Term.query.order_by(Term.year.asc, Term.season_id.asc).all()
	if not asc:
		results.reverse()
	return results

def getAllYears(asc=True):
	results = []
	[results.append(t[0]) for t in Term.query.with_entities(Term.year) if t[0] not in results]
	results.sort()
	if not asc:
		results.reverse()
	return results

def getCurrentTerm():
	for term in Term.query.order_by(Term.end.desc()).all():
		if term.isCurrent():
			return term
	return None

def getAllUserIds():
	return [u[0] for u in User.query.with_entities(User.id)]

def userExists(ucid):
	return ucid in getAllUserIds()

def getSubjectByCode(subjCode):
	return Subject.query.filter_by(code=subjCode.upper()).first()

def getCourseByCode(subjCode, courseCode):
	subject = getSubjectByCode(subjCode)
	if not subject:
		return None
	return Course.query.filter_by(subject_id=subject.id, code=courseCode).first()
