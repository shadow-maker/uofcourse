from app import db
from app.auth import current_user

from flask import Blueprint, request

me_planner = Blueprint("planner", __name__, url_prefix="/planner")

#
# GET
#

@me_planner.route("/progress")
def getPlannerProgress():
	return {
		"courses_taken": len(current_user.coursesTaken),
		"courses_planned": len(current_user.coursesPlanned),
		"units_taken": current_user.unitsTaken,
		"units_planned": current_user.unitsPlanned,
		"units_needed": current_user.unitsNeeded
	}, 200

@me_planner.route("/summary")
def getPlannerSummary():
	results = {}

	x = request.args.get("x").lower()
	y = request.args.get("y").lower()
	taken = request.args.get("taken", "true").lower()
	planned = request.args.get("planned", "true").lower()
	show = request.args.get("show", "courses").lower()

	options = {
		"subjects": lambda cc : cc.course.subject_code,
		"faculties": lambda cc : None if cc.isCustom() else cc.course.subject.faculty.subdomain or cc.course.subject.faculty.name,
		"levels": lambda cc : f"{cc.course.level}XX",
		"grades": lambda cc : cc.grade.symbol if cc.grade_id else "none",
		"terms": lambda cc : str(cc.collection.term_id) if cc.collection.term_id else "none"
	}

	if x not in options:
		return {"error": "invalid x option"}, 400

	if taken not in ["true", "1", "false", "0"]:
		return {"error": "invalid taken option"}, 400
	taken = taken in ["true", "1"]

	if planned not in ["true", "1", "false", "0"]:
		return {"error": "invalid planned option"}, 400
	planned = planned in ["true", "1"]

	if show not in ["courses", "units"]:
		return {"error": "show must be either courses or units"}, 400

	getX = options[x]
	keysX = set()

	if not y:
		results["total"] = 0
		for cc in current_user.courses:
			if planned == cc.collection.isPlanned() or taken == cc.collection.isTaken():
				tempX = getX(cc)
				keysX.add(tempX)
				if tempX not in results:
					results[tempX] = 1 if show == "courses" else cc.course.units
				else:
					results[tempX] += 1 if show == "courses" else cc.course.units
				results["total"] += 1 if show == "courses" else cc.course.units

		return {
			"x_keys": sorted(list(keysX)) + ["total"],
			"results": results
		}, 200

	if y not in options:
		return {"error": "invalid y option"}, 400
	if x == y:
		return {"error": "x and y options cannot be the same"}, 400

	getY = options[y]
	keysY = set()

	results["total"] = {"total": 0}

	for cc in current_user.courses:
		if planned == cc.collection.isPlanned() or taken == cc.collection.isTaken():
			tempX = getX(cc)
			tempY = getY(cc)

			keysX.add(tempX)
			keysY.add(tempY)

			if tempX not in results:
				results[tempX] = {"total": 0}
			if tempY not in results[tempX]:
				results[tempX][tempY] = 0
			if tempY not in results["total"]:
				results["total"][tempY] = 0

			results[tempX][tempY] += 1 if show == "courses" else cc.course.units
			results[tempX]["total"] += 1 if show == "courses" else cc.course.units

			results["total"][tempY] += 1 if show == "courses" else cc.course.units
			results["total"]["total"] += 1 if show == "courses" else cc.course.units

	return {
		"x_keys": sorted(list(keysX)) + ["total"],
		"y_keys": sorted(list(keysY)) + ["total"],
		"results": results
	}, 200


@me_planner.route("/warnings")
def getPlannerWarnings():
	missingGradeWarnings = []
	notAvailableWarnings = []
	courseRepeatWarnings = []

	courseRepeats = {}

	for col in current_user.collections:
		if col.isTaken():
			nograde = 0
			for cc in col.collectionCourses:
				if cc.grade is None:
					nograde += 1
				if not cc.isCalendarAvailable():
					notAvailableWarnings.append(
						f"{cc.course_code} was not available in the {col.term.name.capitalize()} term calendar"
					)
				if not cc.course.repeat:
					if cc.course in courseRepeats:
						courseRepeats[cc.course] += 1
					else:
						courseRepeats[cc.course] = 1
			if nograde > 0:
				missingGradeWarnings.append(
					f"Transferred term is missing grades in {nograde} course(s)"
					if col.transfer else
					f"Previous term {col.term.name.capitalize()} is missing grades in {nograde} course(s)"
				)

	for course, count in courseRepeats.items():
		if count > 1:
			courseRepeatWarnings.append(f"{course.code} was taken {count} times and cannot be repeated for credit")

	return {
		"warnings": notAvailableWarnings + courseRepeatWarnings + missingGradeWarnings
	}, 200

#
# PUT
#

@me_planner.route("/progress", methods=["PUT"])
def putUnitsNeeded(unitsNeeded=None):
	if unitsNeeded is None:
		try:
			unitsNeeded = float(request.json["units_needed"])
		except:
			return {"error": "invalid units_needed value"}, 400
	try:
		current_user.units = unitsNeeded
		db.session.commit()
	except:
		return {"error": "failed to update units needed"}, 400
	return {"success": True}, 200