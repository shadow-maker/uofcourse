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

def getSubject(subjCode):
	return Subject.query.filter_by(code=subjCode.upper()).first()

def getCourseById(_subjId, _courseCode):
	return Course.query.filter_by(subject_id=_subjId, code=_courseCode).first()

def getCourseByCode(subjCode, courseCode):
	subject = getSubject(subjCode)
	if not subject:
		return None
	return getCourseById(subject.id, courseCode)

def filterCourses(levels, faculties, subjects, page=1, sortBy=[Course.code, Course.name], perPage=20):
	subjects = [s for s in subjects if Subject.query.filter_by(id=s).first().faculty_id in faculties]
	query = Course.query.filter(Course.level.in_(levels), Course.subject_id.in_(subjects)).order_by(*sortBy)
	return query.paginate(per_page=perPage, page=page)
