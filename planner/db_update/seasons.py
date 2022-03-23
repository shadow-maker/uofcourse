from planner.models import db, Season

def update():
	seasons = ["winter", "spring", "summer", "fall"]

	for i in range(len(seasons)):
		sId = i + 1
		s = Season.query.filter_by(id=sId).first()
		if s:
			print(f"SEASON {sId} ALREADY EXISTS")
			if s.name != seasons[i]:
				print(f"  - name does not match: (db) {s.name} != {seasons[i]}, updating...")
				s.name = seasons[i]
				db.session.commit()
		else:
			print(f"CREATING SEASON {sId}")
			s = Season(id=sId, name=seasons[i])
			db.session.add(s)
			db.session.commit()
