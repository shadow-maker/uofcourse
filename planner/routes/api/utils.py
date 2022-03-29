from planner import queryUtils as utils
from planner.constants import *
from planner.models import Course, Subject

from flask import request

def getById(table, id):
	obj = utils.getById(table, id)
	if not obj:
		return {"error": f"{table.__name__} with id {id} does not exist"}, 404
	return dict(obj), 200


def getAll(table, filters=(), serializer=None):
	if not serializer:
		serializer = lambda item: dict(item)

	if not callable(serializer):
		return {"error": "serializer must be a function"}, 400

	data = {
		"sort": request.args.getlist("sort" + "[]", type=str),
		"asc": request.args.get("asc", default="true", type=str).lower(),
		"limit": request.args.get("limit", default=30, type=int),
		"page": request.args.get("page", default=1, type=int)
	}

	sortBy = []
	for column in data["sort"]:
		try:
			sortBy.append(getattr(table, column))
		except:
			return {"error": f"'{column}' is not a valid column for {table.__tablename__}"}, 400
	if table.id not in sortBy:
		sortBy.append(table.id)

	if data["asc"] not in ["true", "1", "false", "0"]:
		return {"error": f"'{data['asc']}' is not a valid value for asc (boolean)"}, 400

	if data["asc"] in ["false", "0"]:
		sortBy = [i.desc() for i in sortBy]
	
	for i in ["page", "limit"]:
		if data[i] < 1:
			return {"error": f"{i} cannot be lower than 1 (got {data[i]})"}, 400

	if data["limit"] > MAX_ITEMS_PER_PAGE:
		return {"error": f"limit of items per page cannot be greater than {MAX_ITEMS_PER_PAGE}"}, 400

	try:
		query = table.query.filter(*filters).order_by(*sortBy)
	except:
		return {"error": "filters are not valid"}, 400

	results = query.paginate(per_page=data["limit"], page=data["page"])

	return {
		"results": [serializer(i) for i in results.items],
		"page": data["page"],
		"pages": results.pages,
		"total": results.total
	}, 200