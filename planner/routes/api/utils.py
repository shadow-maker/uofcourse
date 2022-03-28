from planner import queryUtils as utils
from planner.constants import *
from planner.models import Course, Subject

COURSE_SORT_OPTIONS = [
	[Course.code, Course.name],
	[Course.name, Course.code]
]

SUBJECT_SORT_OPTIONS = [
	[Subject.code, Subject.name],
	[Subject.name, Subject.code]
]

def getById(table, id):
	obj = utils.getById(table, id)
	if not obj:
		return {"error": f"{table.__name__} with id {id} does not exist"}, 404
	return dict(obj), 200


def getAll(table, args):
	data = {
		"sort": args.get("sort", default="id", type=str).lower(),
		"asc": args.get("asc", default="true", type=str).lower(),
		"limit": args.get("limit", default=30, type=int),
		"page": args.get("page", default=1, type=int)
	}

	try:
		column = getattr(table, data["sort"])
	except:
		return {"error": f"'{data['sort']}' is not a valid column for {table.__tablename__}"}, 400

	if data["asc"] not in ["true", "1", "false", "0"]:
		return {"error": f"'{data['asc']}' is not a valid value for asc (boolean)"}, 400
	

	if data["asc"] in ["false", "0"]:
		column = table.id.desc()
	
	for i in ["page", "limit"]:
		if data[i] < 1:
			return {"error": f"{i} cannot be lower than 1 (got {data[i]})"}, 400

	if data["limit"] > MAX_ITEMS_PER_PAGE:
		return {"error": f"limit of items per page cannot be greater than {MAX_ITEMS_PER_PAGE}"}, 400

	results = table.query.order_by(column).paginate(per_page=data["limit"], page=data["page"])

	return {
		"results": [dict(i) for i in results.items],
		"page": data["page"],
		"pages": results.pages,
		"total": results.total
	}, 200