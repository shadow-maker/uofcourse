from app.models import CourseCollection
from app.auth import current_user

from flask import Blueprint, request
from sqlalchemy import desc
from sqlalchemy.orm.attributes import QueryableAttribute

me_collection = Blueprint("collections", __name__, url_prefix="/collections")

#
# GET
#

@me_collection.route("")
def getCourseCollections():
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
def getCourseCollection(id):
	collection = CourseCollection.query.filter_by(id=id).first()

	if not collection:
		return {"error": f"CourseCollection does not exist"}, 404

	if collection.user_id != current_user.id:
		return {"error": f"User (#{current_user.id}) does not have access to this CourseCollection"}, 403
	
	return dict(collection), 200

@me_collection.route("/<id>/courses")
def getCourseCollectionCourses(id):
	collection = CourseCollection.query.filter_by(id=id).first()

	if not collection:
		return {"error": f"CourseCollection does not exist"}, 404

	if collection.user_id != current_user.id:
		return {"error": f"User (#{current_user.id}) does not have access to this CourseCollection"}, 403
	
	return {"courses": [dict(course) for course in collection.userCourses]}, 200

@me_collection.route("/<id>/gpa")
def getCourseCollectionGpa(id, precision=3):
	collection = CourseCollection.query.filter_by(id=id).first()

	if not collection:
		return {"error": f"CourseCollection does not exist"}, 404

	if collection.user_id != current_user.id:
		return {"error": f"User (#{current_user.id}) does not have access to this CourseCollection"}, 403
	
	return {
		"points": collection.getPoints(precision),
		"units": collection.units,
		"gpa": collection.getGPA(precision)
	}, 200

#
# DELETE
#

# CourseCollection

# @me_collection.route("/collection", defaults={"id":None}, methods=["DELETE"])
# @me_collection.route("/collection/<id>", methods=["DELETE"])
# def delCourseCollection(data={}, id=None):
# 	if not id:
# 		if not data:
# 			data = request.get_json()
# 		if not data:
# 			data = request.form.to_dict()
# 		if not data:
# 			return {"error": "no data provided"}, 400
# 		if not "id" in data:
# 			return {"error": "no CourseCollection id provided"}, 400
# 		id = data["id"]

# 	collection = CourseCollection.query.filter_by(id=id).first()

# 	if not collection:
# 		return {"error": f"CourseCollection does not exist"}, 404

# 	if collection.user_id != current_user.id:
# 		return {"error": f"User (#{current_user.id}) does not have access to this CourseCollection"}, 403
	
# 	if collection.userCourses:
# 		return {"error": f"CourseCollection is not empty"}, 400

# 	db.session.delete(collection)
# 	db.session.commit()

# 	return {"success": True}, 200
