from planner.models import Term, Subject, Course

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
	for term in Term.query.order_by(Term.end.desc()).all():
		if term.isPrev():
			return term
	return None

def getCurrentTerm():
	for term in Term.query.order_by(Term.end.desc()).all():
		if term.isCurrent():
			return term
	return None

def getNextTerm():
	for term in Term.query.order_by(Term.start.asc()).all():
		if term.isNext():
			return term
	return None

def getSubjectByCode(subjectCode):
	return Subject.query.filter_by(code=subjectCode.upper()).first()

def getCourseByCode(subjectCode, courseNumber):
	subject = getSubjectByCode(subjectCode)
	if not subject:
		return None
	return Course.query.filter_by(subject_id=subject.id, code=courseNumber).first()
