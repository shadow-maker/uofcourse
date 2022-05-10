from app.models import Term, Subject, Course
from app.localdt import local

from typing import Union

def getAllTerms(asc: bool = True) -> list[Term]:
	order = [Term.year, Term.season]
	if not asc:
		order = [i.desc() for i in order]
	return Term.query.order_by(*order).all()

def getAllYears(asc: bool =True) -> list[int]:
	order = [Term.year]
	if not asc:
		order = [i.desc() for i in order]
	return list(set([t[0] for t in Term.query.with_entities(Term.year).order_by(*order)]))

def getPrevTerm() -> Union[Term, None]:
	today = local.date()
	for term in Term.query.order_by(Term.end.desc()).all():
		if term.isPrev(today):
			return term
	return None

def getCurrentTerm() -> Union[Term, None]:
	today = local.date()
	for term in Term.query.order_by(Term.end.desc()).all():
		if term.isCurrent(today):
			return term
	return None

def getNextTerm() -> Union[Term, None]:
	today = local.date()
	for term in Term.query.order_by(Term.start.asc()).all():
		if term.isNext(today):
			return term
	return None

def getSubjectByCode(subjectCode: str) -> Union[Subject, None]:
	return Subject.query.filter_by(code=subjectCode.upper()).first()

def getCourseByCode(subjectCode: str, courseNumber: Union[str, int]) -> Union[Course, None]:
	subject = getSubjectByCode(subjectCode)
	if not subject:
		return None
	return Course.query.filter_by(subject_id=subject.id, code=courseNumber).first()
