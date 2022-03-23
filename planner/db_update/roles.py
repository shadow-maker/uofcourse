from planner.models import db, Role

def update():
	roles = {
		1 : "user",
		2 : "moderator",
		3 : "admin"
	}

	for id, name in roles.items():
		role = Role.query.filter_by(id=id).first()
		if role:
			print(f"ROLE {id} ALREADY EXISTS")
			if role.name != name:
				print(f"  - name does not match: (db) {role.name} != {name}, updating...")
				role.name = name
				db.session.commit()
		else:
			print(f"CREATING ROLE {id}")
			role = Role(id=id, name=name)
			db.session.add(role)
			db.session.commit()
