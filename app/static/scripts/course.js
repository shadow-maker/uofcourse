//
// REQUEST FUNCTIONS
//

function requestCourseTags(callback) {
	requestTag("/course/" + course_id, "GET", {}, callback)
}

function requestCollectionCourses(callback) {
	$.ajax({
		url: "/api/me/courses/course/" + course_id,
		method: "GET",
		success: callback,
		error: displayError
	})
}

function requestCollectionTerm(id, callback) {
	$.ajax({
		url: "/api/me/collections/" + id + "/term",
		method: "GET",
		success: callback,
		error: displayError
	})
}

function toggleTag(id) {
	requestTag("/" + id + "/course/" + course_id, "PUT", {}, (data) => {
		alert("success", data.success)
		updateTags()
	})
}

function addCollection(id) {
	console.log("Adding to collection " + id)
	$.ajax({
		url: "/api/me/courses",
		method: "POST",
		data: {
			course_id: course_id,
			collection_id: id
		},
		success: (response) => {
			alert("success", "Added Course to Term")
			updateCollections()
		},
		error: displayError
	})
}

//
// UPDATE FUNCTIONS
//

function updateTags() {
	$("#tags").find(".loading").show()

	// Add dropdown items
	$("#tags").find(".tags-dropdown").empty()
	for (let tag of tags) {
		let tagDropItem = $("#templates .tags-dropdown-item").clone()

		tagDropItem.attr("db-id", tag.id)
		tagDropItem.find(".tag-name").text(tag.name)

		tagDropItem.on("click", () => {
			toggleTag(tag.id)
		})

		$("#tags").find(".tags-dropdown").append(tagDropItem)
	}

	// Request course tags and add selected tags
	requestCourseTags((data) => {
		$("#tags").find(".loading").hide()

		$("#tags").find(".tags-selected").empty()
		for (let tag of data.tags) {
			let tagItem = $("#templates .tag-selected-item").clone()

			tagItem.find(".tag-name").text(tag.name)

			if (tag.emoji) {
				tagItem.find(".tag-emoji").html("&#" + tag.emoji)
				tagItem.find(".tag-emoji").removeClass("d-none")
			} else {
				tagItem.find(".tag-color").css("color", "#" + tag.color_hex)
				tagItem.find(".tag-color").removeClass("d-none")
			}

			tagItem.on("click", () => {
				toggleTag(tag.id)
			})

			$("#tags").find(".tags-selected").append(tagItem)
		}

		$("#tags").find(".tags-dropdown-item").each(function () {
			if (data.tags.find(t => t.id == parseInt($(this).attr("db-id"))))
				$(this).find(".bi-check").removeClass("invisible")
			else
				$(this).find(".bi-check").addClass("invisible")
		})
	})
}

function updateCollections() {
	$("#collections").find(".loading").show()
	$("#collections").find(".loaded").hide()

	requestCollectionCourses((data) => {
		$("#collections").find(".loading").hide()
		$("#collections").find(".loaded").show()

		$("#collections").find(".collections-container .list-group").empty()
		if (data.results.length > 0)
		$("#collections").find(".collections-container").removeClass("d-none")
		else
		$("#collections").find(".collections-none").removeClass("d-none")
		for (let cc of data.results) {
			let collecCourseItem = $("#templates .collection-course-item").clone()

			collecCourseItem.attr("href", "/planner?id=" + cc.id)

			requestCollectionTerm(cc.collection_id, (term) => {
				if (term.transfer)
					collecCourseItem.find(".term-name").text("Transfer")
				else
					collecCourseItem.find(".term-name").text(
						term.season.charAt(0).toUpperCase() + term.season.slice(1) + " " + term.year
					)
			})

			if (cc.grade_id) {
				let grade = grades[cc.grade_id]
				collecCourseItem.find(".grade").text(grade.symbol)
				collecCourseItem.find(".grade").attr(
					"title", grade.gpv + " GPV | " + cc.weightedGPV + " Weighted"
				)
			} else {
				collecCourseItem.find(".grade").text("-")
				collecCourseItem.find(".grade").attr("title", "Grade not set")
			}

			$("#collections").find(".collections-container .list-group").append(collecCourseItem)
		}

		$("#collections").find(".collections-dropdown-item").each(function () {
			if (data.results.find(c => c.collection_id == parseInt($(this).attr("db-id")))) {
				$(this).find(".bi-check").removeClass("invisible")
				$(this).find(".dropdown-item").on("click", () => {})
			} else {
				$(this).find(".bi-check").addClass("invisible")
				$(this).find(".dropdown-item").on("click", (e) => {
					e.preventDefault()
					e.stopImmediatePropagation()
					addCollection($(this).attr("db-id"))
				})
			}
		})
	})
}

//
// DOCUMENT READY
//

$(document).ready(() => {
	tagsInit(() => {
		updateTags()
		updateCollections()
	})
})
