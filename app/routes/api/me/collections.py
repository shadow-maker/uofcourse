from app import db
from app.models import CourseCollection, Term, Season, Course
from app.auth import current_user

from flask import Blueprint, request
from sqlalchemy import desc
from sqlalchemy.orm.attributes import QueryableAttribute

from app.models.user_course import UserCourse

me_collection = Blueprint("collections", __name__, url_prefix="/collections")

#
# GET
#

@me_collection.route("")
def getCollections():
	sort = list(dict.fromkeys(request.args.getlist("sort", type=str)))
	asc = request.args.get("asc", default="true", type=str).lower()

	# Get list of table columns for sorting
	order = []
	for column in sort:
		try:
			col = getattr(CourseCollection, column)
			if not issubclass(type(col), QueryableAttribute):
				raise AttributeError
		except AttributeError:
			return {"error": f"'{column}' is not a valid column for CourseCollection"}, 400
		order.append(col)
	order.append(CourseCollection.id)

	# Add sorting columns to desc() if asc is false
	if asc in ["false", "0"]:
		order = [desc(i) for i in order]

	# Query database
	try:
		results = CourseCollection.query.filter_by(user_id=current_user.id).order_by(*order).all()
	except:
		return {"error": "sort columns are not valid"}, 400
		
	return {"collections": [dict(collection) for collection in results]}, 200

@me_collection.route("/<id>")
def getCollection(id):
	collection = CourseCollection.query.filter_by(id=id, user_id=current_user.id).first()

	if not collection:
		return {"error": f"CourseCollection from this user does not exist"}, 404

	return dict(collection), 200

@me_collection.route("/<id>/term")
def getCollectionTerm(id):
	collection = CourseCollection.query.filter_by(id=id, user_id=current_user.id).first()

	if not collection:
		return {"error": f"CourseCollection from this user does not exist"}, 404

	return {"transfer": True} if collection.transfer else dict(collection.term), 200

@me_collection.route("/<id>/courses")
def getCollectionCourses(id):
	collection = CourseCollection.query.filter_by(id=id, user_id=current_user.id).first()

	if not collection:
		return {"error": f"CourseCollection from this user does not exist"}, 404

	sort = list(dict.fromkeys(request.args.getlist("sort", type=str)))
	asc = request.args.get("asc", default="true", type=str).lower()

	# Get list of table columns for sorting
	order = []
	for column in sort:
		try:
			col = getattr(UserCourse, column)
			if not issubclass(type(col), QueryableAttribute):
				raise AttributeError
		except AttributeError:
			return {"error": f"'{column}' is not a valid column for UserCourse"}, 400
		order.append(col)
	order.append(UserCourse.id)

	# Add sorting columns to desc() if asc is false
	if asc in ["false", "0"]:
		order = [desc(i) for i in order]

	# Query database
	try:
		results = UserCourse.query.filter_by(course_collection_id=id).order_by(*order).all()
	except:
		return {"error": "sort columns are not valid"}, 400
	
	return {"courses": [dict(uc) for uc in results]}, 200

@me_collection.route("/course/<id>")
def getCourseCollections(id):
	course = Course.query.get(id)
	if not course:
		return {"error": f"Course with id {id} does not exist"}, 404
	return {
		"collections": [
			dict(collection) for collection in current_user.collections if course in collection.courses
		]
	}, 200

#
# POST
#

@me_collection.route("", methods=["POST"])
def postCollection(data={}):
	if not data:
		data = request.form.to_dict()
		if not data:
			return {"error": "no data provided"}, 400

	if "term" in data:
		term = Term.query.filter_by(term_id=data["term"]).first()
	elif ("season" in data) and ("year" in data):
		try:
			if data["season"].isdigit():
				season = Season(int(data["season"]))
			else:
				season = getattr(Season, data["season"])
		except:
			return {"error": "season not found"}, 400
		term = Term.query.filter_by(season=season, year=data["year"]).first()
	else:
		return {"error": "term not specified"}, 400

	if not term:
		return {"error": "term does not exist"}, 400

	if CourseCollection.query.filter_by(user_id=current_user.id, term_id=term.id).first():
		return {"error": f"User already has a collection for term {term.name.capitalize()}"}, 400

	try:
		collection = CourseCollection(current_user.id, term.id)
		db.session.add(collection)
		db.session.commit()
	except:
		return {"error": "failed to create collection"}, 500
	
	return {"success": True}, 200

#
# DELETE
#

# CourseCollection

@me_collection.route("/<id>", methods=["DELETE"])
def delCollection(id):
	collection = CourseCollection.query.filter_by(id=id, user_id=current_user.id).first()

	if not collection:
		return {"error": f"CourseCollection from this user does not exist"}, 404

	if collection.userCourses:
		return {"error": f"CourseCollection is not empty"}, 400

	try:
		db.session.delete(collection)
		db.session.commit()
	except:
		return {"error": "failed to delete collection"}, 500

	return {"success": True}, 200
