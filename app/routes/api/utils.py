from app.constants import *
from sqlalchemy.orm.attributes import QueryableAttribute

from flask import request


def getById(table, id):
	obj = table.query.get(id)
	if not obj:
		return {"error": f"{table.__name__} with id {id} does not exist"}, 404
	return dict(obj), 200


def getAll(table, filters=(), serializer=None):
	if not serializer: # default serializer
		serializer = lambda item : dict(item)

	# Validate filters and serializer
	if type(filters) != tuple:
		return {"error": "filters must be of type tuple"}, 400
	if not callable(serializer):
		return {"error": "serializer must be a function"}, 400

	# Get data from url arguments
	sort = list(dict.fromkeys(request.args.getlist("sort", type=str)))
	asc = request.args.get("asc", default="true", type=str).lower()
	limit = request.args.get("limit", default=30, type=int)
	page = request.args.get("page", default=1, type=int)

	# Validate data
	if asc not in ["true", "1", "false", "0"]:
		return {"error": f"'{asc}' is not a valid value for asc (boolean)"}, 400
	if limit < 1:
		return {"error": f"limit of items per page cannot be lower than 1 (got {limit})"}, 400
	if limit > MAX_ITEMS_PER_PAGE:
		return {"error": f"limit of items per page cannot be greater than {MAX_ITEMS_PER_PAGE}"}, 400
	if page < 1:
		return {"error": f"page cannot be lower than 1 (got {page})"}, 400

	# Get list of table columns for sorting
	sortBy = []
	for column in sort:
		try:
			col = getattr(table, column)
			if not issubclass(type(col), QueryableAttribute):
				raise AttributeError
		except AttributeError:
			return {"error": f"'{column}' is not a valid column for {table.__tablename__}"}, 400
		sortBy.append(col)
	if table.id not in sortBy:
		sortBy.append(table.id)

	# Add .desc() to sorting columns if asc is false
	if asc in ["false", "0"]:
		sortBy = [i.desc() for i in sortBy]

	# Query database with filters
	try:
		query = table.query.filter(*filters)
	except:
		return {"error": "filters are not valid"}, 400
	try:
		query = query.order_by(*sortBy)
	except:
		return {"error": "sort columns are not valid"}, 400

	# Get  results
	results = query.paginate(per_page=limit, page=page)

	return {
		"results": [serializer(i) for i in results.items], # pass every result item through serializer
		"page": results.page,
		"pages": results.pages,
		"total": results.total
	}, 200
