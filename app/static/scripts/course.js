//
// REQUEST FUNCTIONS
//

function requestCourseTags(callback) {
	ajax("GET", "me/tags/course/" + course_id, {}, callback)
}

function requestCollectionCourses(callback) {
	ajax("GET", "me/courses/course/" + course_id, {}, callback)
}

function requestCollectionTerm(id, callback) {
	ajax("GET", "me/collections/" + id + "/term", {}, callback)
}

function toggleTag(id) {
	ajax("PUT", "me/tags/" + id + "/course/" + course_id, {}, (data) => {
		alert("success", data.success)
		updateTags()
	})
}

function addCollection(id) {
	ajax("POST", "me/courses",
		{
			course_id: course_id,
			collection_id: id
		},
		(response) => {
			alert("success", "Added Course to Term")
			for (let w of response.warnings)
				alert("warning", w)
			updateCollections()
		}
	)
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
	$("#collections").find(".collections-container").addClass("d-none")
	$("#collections").find(".collections-none").addClass("d-none")

	requestCollectionCourses((data) => {
		$("#collections").find(".loading").hide()

		$("#collections").find(".collections-container .list-group").empty()
		if (data.results.length > 0) {
			$("#collections").find(".collections-container").removeClass("d-none")
			$("#collections").find(".collections-none").addClass("d-none")
		} else {
			$("#collections").find(".collections-container").addClass("d-none")
			$("#collections").find(".collections-none").removeClass("d-none")
		}
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
			let cc = data.results.find(c => c.collection_id == parseInt($(this).attr("db-id")))
			if (cc) {
				$(this).find(".bi-check").removeClass("invisible")
				$(this).find(".dropdown-item").off("click")
				if (cc.calendar_available)
					$(this).find(".warning").addClass("invisible")
				else
					$(this).find(".warning").removeClass("invisible")
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
