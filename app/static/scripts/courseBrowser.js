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

//
// REQUEST FUNCS
//

function requestCourseTags(id, callback) {
	requestTag("/course/" + id, "GET", {}, callback)
}

function requestCourseCollections(id, callback) {
	$.ajax({
		url: "/api/me/collections/course/" + id,
		method: "GET",
		success: callback,
		error: displayError
	})
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
	if (number != null)
		data.number = number
	if (repeat != null)
		data.repeat = repeat
	if (countgpa != null)
		data.countgpa = countgpa

	if (JSON.stringify(data) == JSON.stringify(prevQuery))
		return

	prevQuery = data

	$(".loading").show()
	$(".loaded").hide()

	$.ajax({
		url: "/api/courses",
		method: "GET",
		data: data,
		traditional: true,
		success: callback,
		error: (response) => {
			$(".loading").hide()
			displayError(response)
		}
	})
}

function toggleCourseTag(courseId, tagId) {
	requestTag("/" + tagId +"/course/" + courseId, "PUT", {}, (response) => {
		alert("success", response.success)
		let course = coursesData.find(c => c.id == courseId)
		requestCourseTags(courseId, (data) => {
			course.tags = data.tags.map(tag => tag.id)
			updateCourseTags(courseId)
		})
	})
}

function addCollection(courseId, collectionId) {
	$.ajax({
		url: "/api/me/courses",
		method: "POST",
		data: {
			course_id: courseId,
			collection_id: collectionId
		},
		success: (response) => {
			alert("success", "Added Course to Term")
			let course = coursesData.find(c => c.id == courseId)
			requestCourseCollections(courseId, (data) => {
				course.collections = data.collections.map(c => c.id)
				updateCourseCollections(courseId)
			})
		},
		error: displayError
	})
}

//
// UPDATE FUNCS
//

function updateResults(data) {
	$(".loading").hide()
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

	// Add content only available if user is authenticated
	if (isAuth) {
		// Add tag dropdown items to tag dropdown
		course.element.find(".tags-dropdown").empty()
		for (let tag of userTags) {
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
		updateCourseCollections(id)
	} else {
		course.element.find(".tags-dropdown-btn").on("click", function(e) {
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
	const tags = course.element.find(".course-tags")

	tags.find(".tags-selected").empty()
	for (let tagId of course.tags) {
		let tag = userTags.find(t => t.id == tagId)
			
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

		tags.find(".tags-selected").append(tagItem)
	}

	tags.find(".tags-dropdown-item").each(function () {
		if (course.tags.includes(parseInt($(this).attr("db-id"))))
			$(this).find(".bi-check").removeClass("invisible")
		else
			$(this).find(".bi-check").addClass("invisible")
	})
}

function updateCourseCollections(id) {
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
			$(this).find(".dropdown-item").on("click", () => {})
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
