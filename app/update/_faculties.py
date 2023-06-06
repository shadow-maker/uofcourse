from . import _subjects, logger
from app.models import db, Calendar, Faculty

from bs4 import ResultSet

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
	logger.info(f"Found {len(items)} Faculty items")
	for f in items:
		# Get Faculty name data
		name = f.find(class_="generic-title").text.strip()
		logger.debug(f"Reading Faculty with name '{name}'")

		if name in FACULTY_MAPPINGS:
			name = FACULTY_MAPPINGS[name]
			logger.debug(f"Found alternative name in mappings, replacing with '{name}'")

		# Check for existing Faculty
		faculty = Faculty.query.filter(Faculty.name.ilike(name)).first()
		if faculty is not None:
			logger.debug(f"Faculty (id {faculty.id}) already exists (skipping)")
		else: # Create new Faculty
			logger.debug("Faculty does not exist (creating)")
			try:
				faculty = Faculty(name=name)
				db.session.add(faculty)
			except Exception as e:
				logger.error(f"Failed to create Faculty with name '{name}':\n{e}")
			try:
				db.session.commit()
			except Exception as e:
				logger.error(f"Failed to commit Faculty with name '{name}':\n{e}")

		# Get all Subject links
		subjectItems = f.find(class_="generic-body").find_all("a")

		_subjects.update(calendar, faculty.id, subjectItems)
