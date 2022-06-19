from app import db
from app.models import Collection, CollectionCourse, Term, Season, Course
from app.auth import current_user

from flask import Blueprint, request
from sqlalchemy import desc
from sqlalchemy.orm.attributes import QueryableAttribute

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
			col = getattr(Collection, column)
			if not issubclass(type(col), QueryableAttribute):
				raise AttributeError
		except AttributeError:
			return {"error": f"'{column}' is not a valid column for Collection"}, 400
		order.append(col)
	order.append(Collection.id)

	# Add sorting columns to desc() if asc is false
	if asc in ["false", "0"]:
		order = [desc(i) for i in order]

	# Query database
	try:
		results = Collection.query.filter_by(user_id=current_user.id).order_by(*order).all()
	except:
		return {"error": "sort columns are not valid"}, 400
		
	return {"collections": [dict(collection) for collection in results]}, 200

@me_collection.route("/<id>")
def getCollection(id):
	collection = Collection.query.filter_by(id=id, user_id=current_user.id).first()

	if not collection:
		return {"error": f"Collection from this user does not exist"}, 404

	return dict(collection), 200

@me_collection.route("/<id>/term")
def getCollectionTerm(id):
	collection = Collection.query.filter_by(id=id, user_id=current_user.id).first()

	if not collection:
		return {"error": f"Collection from this user does not exist"}, 404

	return {"transfer": True} if collection.transfer else dict(collection.term), 200

@me_collection.route("/<id>/courses")
def getCollectionCourses(id):
	collection = Collection.query.filter_by(id=id, user_id=current_user.id).first()

	if not collection:
		return {"error": f"Collection from this user does not exist"}, 404

	sort = list(dict.fromkeys(request.args.getlist("sort", type=str)))
	asc = request.args.get("asc", default="true", type=str).lower()

	# Get list of table columns for sorting
	order = []
	for column in sort:
		try:
			col = getattr(CollectionCourse, column)
			if not issubclass(type(col), QueryableAttribute):
				raise AttributeError
		except AttributeError:
			return {"error": f"'{column}' is not a valid column for CollectionCourse"}, 400
		order.append(col)
	order.append(CollectionCourse.id)

	# Add sorting columns to desc() if asc is false
	if asc in ["false", "0"]:
		order = [desc(i) for i in order]

	# Query database
	try:
		results = CollectionCourse.query.filter_by(collection_id=id).order_by(*order).all()
	except:
		return {"error": "sort columns are not valid"}, 400
	
	return {"courses": [dict(cc) for cc in results]}, 200

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
		data = request.json
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

	if Collection.query.filter_by(user_id=current_user.id, term_id=term.id).first():
		return {"error": f"User already has a collection for term {term.name.capitalize()}"}, 400

	try:
		collection = Collection(current_user.id, term.id)
		db.session.add(collection)
		db.session.commit()
	except:
		return {"error": "failed to create collection"}, 500
	
	return {"success": True}, 200

#
# DELETE
#

# Collection

@me_collection.route("/<id>", methods=["DELETE"])
def delCollection(id):
	collection = Collection.query.filter_by(id=id, user_id=current_user.id).first()

	if not collection:
		return {"error": f"Collection from this user does not exist"}, 404

	if collection.collectionCourses:
		return {"error": f"Collection is not empty"}, 400

	try:
		db.session.delete(collection)
		db.session.commit()
	except:
		return {"error": "failed to delete collection"}, 500

	return {"success": True}, 200
