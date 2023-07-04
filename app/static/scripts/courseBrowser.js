//
// GLOBAL VARS
//

var coursesData = []
var prevQuery = {}

// Init Page object (defined in pagination.html)
var page = new Page(0, () => {
	requestResults(updateResults)
})

//
// UTIL FUNCS
//

function uncheckAll(container) {
	$("#" + container + " .form-check").each(function () {
		$(this).find("input").prop("checked", false)
	})
	$("#formFilterCourses").submit()
}

function checkAll(container) {
	$("#" + container + " .form-check").each(function () {
		$(this).find("input").prop("checked", true)
	})
	$("#formFilterCourses").submit()
}

function setRatingIndicator(element, rating) {
	for (let i = 1; i <= 5; i++) {
		let star = element.find(".star-" + i)
		if (i <= rating) {
			star.find(".bi-star").addClass("d-none")
			star.find(".bi-star-half").addClass("d-none")
			star.find(".bi-star-fill").removeClass("d-none")
		} else if (i <= rating + 0.5) {
			star.find(".bi-star").addClass("d-none")
			star.find(".bi-star-half").removeClass("d-none")
			star.find(".bi-star-fill").addClass("d-none")
		} else {
			star.find(".bi-star").removeClass("d-none")
			star.find(".bi-star-half").addClass("d-none")
			star.find(".bi-star-fill").addClass("d-none")
		}
	}
	element.prop("title", rating && rating >= 0 ? rating + " / 5 stars" : "No rating")
}

//
// REQUEST FUNCS
//

function requestCourseTags(id, callback) {
	ajax("GET", "me/tags/course/" + id, {}, callback)
}

function requestCollections(id, callback) {
	ajax("GET", "me/collections/course/" + id, {}, callback)
}

function requestResults(callback) {
	let name = ""
	let number = []

	let words = $("#searchCourses").val().split(" ")
	for (let word of words) {
		if (!isNaN(word) && parseInt(word) >= 100 && parseInt(word) < 800)
			number.push(parseInt(word))
		else
			name += word + " "
	}
	name = name.trim()

	let selectedLevel = []
	$("input[name='selectedLevel']:checked").each(function () {
		selectedLevel.push(parseInt($(this).val()))
	})
	if (selectedLevel.length) {
		$("#levelSelector .check-all-btn").hide()
		$("#levelSelector .uncheck-all-btn").show()
	} else {
		$("#levelSelector .check-all-btn").show()
		$("#levelSelector .uncheck-all-btn").hide()
	}

	let selectedFaculty = []
	$("input[name='selectedFaculty']:checked").each(function () {
		selectedFaculty.push(parseInt($(this).val()))
	})
	if (selectedFaculty.length) {
		$("#facSelector .check-all-btn").hide()
		$("#facSelector .uncheck-all-btn").show()
	} else {
		$("#facSelector .check-all-btn").show()
		$("#facSelector .uncheck-all-btn").hide()
	}

	let selectedSubject = []
	for (let s in subjects)
		if (subjects[s].sel)
			selectedSubject.push(parseInt(subjects[s].id))

	let repeat = JSON.parse($('input[name=repeat]:checked', '#formFilterCourses').val())
	let countgpa = JSON.parse($('input[name=countgpa]:checked', '#formFilterCourses').val())
	let old = JSON.parse($('input[name=old]:checked', '#formFilterCourses').val())

	let data = {
		sort: sortOptions[$("#sortBy").val()].value,
		asc: $("#orderBy").val(),
		level: selectedLevel,
		faculty: selectedFaculty,
		subject: selectedSubject,
		page: page.current
	}

	if (name.length > 0)
		data.name = name
	if (number.length > 0)
		data.number = number
	if (repeat != null)
		data.repeat = repeat
	if (countgpa != null)
		data.countgpa = countgpa
	if (old != null)
		data.old = old

	if (JSON.stringify(data) == JSON.stringify(prevQuery))
		return

	prevQuery = data

	$(".loading").show()
	$(".loaded").hide()

	ajax("GET", "courses", data, callback, displayError, () => { $(".loading").hide() })
}

function toggleCourseTag(courseId, tagId) {
	ajax("PUT", "me/tags/" + tagId + "/course/" + courseId, {}, (response) => {
		alert("success", response.success)
		let course = coursesData.find(c => c.id == courseId)
		requestCourseTags(courseId, (data) => {
			course.tags = data.tags.map(tag => tag.id)
			updateCourseTags(courseId)
		})
	})
}

function addCollection(courseId, collectionId) {
	ajax("POST", "me/courses",
		{
			course_id: courseId,
			collection_id: collectionId
		},
		(response) => {
			alert("success", "Added Course to Term")
			let course = coursesData.find(c => c.id == courseId)
			requestCollections(courseId, (data) => {
				course.collections = data.collections.map(c => c.id)
				updateCollections(courseId)
			})
		}
	)
}

//
// UPDATE FUNCS
//

function updateResults(data) {
	$(".loaded").show()

	$("#coursesContainer").empty()

	coursesData = data.results
	for (let course of coursesData) {
		course.element = $("#templates .course-item").clone()
		updateCourse(course.id)
	}

	$(".num-total").text(data.total)

	page.current = data.page
	page.total = data.pages

	page.updateNav()
}

function updateCourse(id) {
	let course = coursesData.find(c => c.id == id)

	course.element.find(".course-link").attr("href", course.url)
	course.element.find(".course-emoji").html("&#" + (course.emoji ? course.emoji : DEFAULT_EMOJI))
	course.element.find(".course-code").text(course.code)
	course.element.find(".course-name").text(course.name)
	setRatingIndicator(course.element.find(".course-rating"), course.rating / 20)
	if (course.rating < 0)
		course.element.find(".course-rating").addClass("text-muted").removeClass("text-warning")
	else
		course.element.find(".course-rating").removeClass("text-muted").addClass("text-warning")
	if (course.old)
		course.element.find(".course-old").removeClass("d-none")

	// Add content only available if user is authenticated
	if (isAuth) {
		// Add tag dropdown items to tag dropdown
		course.element.find(".tags-dropdown").empty()
		for (let tag of tags) {
			let tagDropItem = $("#templates .tags-dropdown-item").clone()

			tagDropItem.attr("db-id", tag.id)
			tagDropItem.find(".tag-name").text(tag.name)

			tagDropItem.on("click", (e) => {
				e.preventDefault()
				e.stopImmediatePropagation()
				toggleCourseTag(course.id, tag.id)
			})

			course.element.find(".tags-dropdown").append(tagDropItem)
		}

		updateCourseTags(id)
		updateCollections(id)
	} else {
		course.element.find(".tags-dropdown-btn").on("click", function (e) {
			$(this).dropdown("hide")
			alert("warning", "You must be logged in to add tags")
		})
	}

	course.element.appendTo("#coursesContainer")
}

function updateSubjects() {
	let subjSearch = $("#subjectSearch").val().toUpperCase()
	$("#subjectSearch").val("")

	if (subjSearch in subjects)
		subjects[subjSearch].sel = true

	$("#subjectSelector").empty()

	for (let s in subjects) {
		if (subjects[s].sel) {
			let subjSearchItem = $("#templates .subject-item").clone()
			subjSearchItem.text(s)

			subjSearchItem.on("click", () => {
				subjects[s].sel = false
				subjSearchItem.remove()
				$("#formFilterCourses").submit()
			})

			$("#subjectSelector").append(subjSearchItem)
		}
	}
}

function updateCourseTags(id) {
	const course = coursesData.find(c => c.id == id)
	const courseTags = course.element.find(".course-tags")

	courseTags.find(".tags-selected").empty()
	for (let tagId of course.tags) {
		let tag = tags.find(t => t.id == tagId)

		if (!tag)
			continue

		let tagItem = $("#templates .tag-selected-item").clone()

		tagItem.find(".tag-name").text(tag.name)

		if (tag.emoji) {
			tagItem.find(".tag-emoji").html("&#" + tag.emoji)
			tagItem.find(".tag-emoji").removeClass("d-none")
		} else {
			tagItem.find(".tag-color").css("color", "#" + tag.color_hex)
			tagItem.find(".tag-color").removeClass("d-none")
		}

		tagItem.on("click", (e) => {
			e.preventDefault()
			e.stopImmediatePropagation()
			toggleCourseTag(id, tag.id)
		})

		courseTags.find(".tags-selected").append(tagItem)
	}

	courseTags.find(".tags-dropdown-item").each(function () {
		if (course.tags.includes(parseInt($(this).attr("db-id"))))
			$(this).find(".bi-check").removeClass("invisible")
		else
			$(this).find(".bi-check").addClass("invisible")
	})
}

function updateCollections(id) {
	const course = coursesData.find(c => c.id == id)
	const collections = course.element.find(".course-collections")

	if (course.collections.length == 0)
		collections.find(".collections-dropdown-btn").text(
			"Not taken"
		)
	else if (course.collections.length == 1)
		collections.find(".collections-dropdown-btn").text(
			"Taken in " + course.collections.length + " term"
		)
	else
		collections.find(".collections-dropdown-btn").text(
			"Taken in " + course.collections.length + " terms"
		)

	collections.find(".collections-dropdown-item").each(function () {
		if (course.collections.includes(parseInt($(this).attr("db-id")))) {
			$(this).find(".bi-check").removeClass("invisible")
			$(this).find(".dropdown-item").on("click", () => { })
		} else {
			$(this).find(".bi-check").addClass("invisible")
			$(this).find(".dropdown-item").on("click", (e) => {
				e.preventDefault()
				e.stopImmediatePropagation()
				addCollection(course.id, $(this).attr("db-id"))
			})
		}
	})
}

//
// DOCUMENT READY
//

$(document).ready(() => {
	if (isAuth) {
		tagsInit(() => {
			requestResults((data) => {
				prevQuery = {}
				updateResults(data)
			})
		})
	} else {
		page.callback()
	}

	updateSubjects()

	$("#subjectSearch").on("keyup", (e) => {
		$("#subjectSearchSuggestions").empty()
		if (e.keyCode == 13) {
			$("#subjectSearch").dropdown("hide")
			$("#formFilterCourses").submit()
			$("#subjectSearch").dropdown("show")
		} else {
			let subjSearch = $("#subjectSearch").val().toUpperCase()
			if (subjSearch.length > 0) {
				for (let s in subjects) {
					if (s.startsWith(subjSearch)) {
						let subjSuggestion = $("#templates .subject-suggestion").clone()
						subjSuggestion.find(".code").text(s)
						subjSuggestion.find(".name").text(subjects[s].name)

						subjSuggestion.on("click", () => {
							$("#subjectSearch").val(s)
							$("#subjectSearchSuggestions").empty()
							$("#formFilterCourses").submit()
						})

						$("#subjectSearchSuggestions").append(subjSuggestion)
					}
				}
			}
		}
	})

	$("#formFilterCourses input").not("#subjectSearch").change(() => {
		$("#formFilterCourses").submit()
	})

	$("#sortSelector select").change(() => {
		$("#formFilterCourses").submit()
	})

	$("#formFilterCourses").on("submit", (event) => {
		event.preventDefault()
		event.stopImmediatePropagation()

		updateSubjects()

		// Remove URL query parameters
		window.history.pushState({}, document.title, window.location.pathname)

		// Switch page and request and update data
		page.switch(1)
	})
})
