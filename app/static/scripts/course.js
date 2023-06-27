//
// REQUEST FUNCTIONS
//

let collections = []

function getCollections(callback) {
	ajax("GET", "me/collections", { sort: ["term_id"] }, callback)
}

function getCourseTags(callback) {
	ajax("GET", "me/tags/course/" + course_id, {}, callback)
}

function getCollectionCourses(callback) {
	ajax("GET", "me/courses/course/" + course_id, {}, callback)
}

function getCollections(callback) {
	ajax("GET", "me/collections", { sort: ["term_id"] }, callback)
}

function getCollectionTerm(id, callback) {
	ajax("GET", "me/collections/" + id + "/term", {}, callback)
}

function toggleTag(id) {
	ajax("PUT", "me/tags/" + id + "/course/" + course_id, {}, (data) => {
		alert("success", data.success)
		updateTags()
	})
}

function postCollection(id) {
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
	getCourseTags((data) => {
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

	getCollections(data => {
		collections = data.collections

		getCollectionCourses(data => {
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
				let collection = collections.find(c => c.id == cc.collection_id)
				let collecCourseItem = $("#templates .collection-course-item").clone()

				getCollectionTerm(cc.collection_id, term => {
					collection.term = term
					collection.term_name = term.transfer
						? "Transfer"
						: term.season.charAt(0).toUpperCase() + term.season.slice(1) + " " + term.year
					collecCourseItem.find(".term-name").text(collection.term_name)
					collecCourseItem.on("click", () => updateModals(cc, collection, collections))
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
					if (cc.calendar_available) {
						$(this).find(".warning").addClass("invisible")
						$(this).find(".warning").removeClass("text-warning")
						$(this).find(".warning").addClass("text-body")
					} else {
						$(this).find(".warning").removeClass("invisible")
						$(this).find(".warning").removeClass("text-body")
						$(this).find(".warning").addClass("text-warning")
					}
				} else {
					$(this).find(".bi-check").addClass("invisible")
					$(this).find(".dropdown-item").on("click", (e) => {
						e.preventDefault()
						e.stopImmediatePropagation()
						postCollection($(this).attr("db-id"))
					})
				}
			})
		})
	})
}

function ccAfterUpdate() {
	updateCollections()
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
