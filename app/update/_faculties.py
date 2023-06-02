from . import _subjects, prints
from app.models import db, Calendar, Faculty

from bs4 import ResultSet

FACULTY_PAGE = "course-by-faculty.html"

FACULTY_MAPPINGS = {
	"Faculty of Communication and Culture": "Faculty of Arts",
	"Faculty of Fine Arts": "Faculty of Arts",
	"Faculty of Humanities": "Faculty of Arts",
	"Faculty of Social Sciences": "Faculty of Arts",
	"Collaborating Faculties": "Faculty of Arts",
	"Faculty of Education": "Werklund School of Education",
	"Faculty of Medicine": "Cumming School of Medicine",
	"Faculty of Environmental Design": "School of Architecture, Planning and Landscape",
	"Architecture, Planning and Landscape, School of": "School of Architecture, Planning and Landscape",
	"Faculty of Veterniary Medicine": "Faculty of Veterinary Medicine"
}

def update(calendar: Calendar, items: ResultSet):
	for f in items:
		# Get Faculty name data
		name = f.find(class_="generic-title").text.strip()

		if name in FACULTY_MAPPINGS:
			name = FACULTY_MAPPINGS[name]

		# Check for existing Faculty
		faculty = Faculty.query.filter(Faculty.name.ilike(name)).first()
		prints(2, f"FACULTY: {name}", False)
		if faculty:
			prints(0, f"ALREADY EXISTS (# {faculty.id}), skipping...")
		else: # Create new Faculty
			prints(0, "creating row...")
			faculty = Faculty(name=name)
			db.session.add(faculty)
			db.session.commit()

		# Get all Subject links
		subjectItems = f.find(class_="generic-body").find_all("a")

		_subjects.update(calendar, faculty.id, subjectItems)
