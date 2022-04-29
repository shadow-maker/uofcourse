from app.models import Term, Subject, Course
from app.localdt import local

def getAllTerms(asc=True):
	results = Term.query.order_by(Term.year.asc, Term.season.asc).all()
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

def getPrevTerm():
	today = local.date()
	for term in Term.query.order_by(Term.end.desc()).all():
		if term.isPrev(today):
			return term
	return None

def getCurrentTerm():
	today = local.date()
	for term in Term.query.order_by(Term.end.desc()).all():
		if term.isCurrent(today):
			return term
	return None

def getNextTerm():
	today = local.date()
	for term in Term.query.order_by(Term.start.asc()).all():
		if term.isNext(today):
			return term
	return None

def getSubjectByCode(subjectCode):
	return Subject.query.filter_by(code=subjectCode.upper()).first()

def getCourseByCode(subjectCode, courseNumber):
	subject = getSubjectByCode(subjectCode)
	if not subject:
		return None
	return Course.query.filter_by(subject_id=subject.id, code=courseNumber).first()
