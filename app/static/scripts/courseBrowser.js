//
// GLOBAL VARS
//

var prevData = {}

// Init Page object (defined in pagination.html)
var page = new Page(0, () => {
	requestResults((data) => {
		updateResults(data)
	})
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

function requestResults(callback, ignorePrev=false) {
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
	
	var data = {
		sort: sortOptions[$("#sortBy").val()].value,
		asc: $("#orderBy").val(),
		name: name,
		level: selectedLevel,
		faculty: selectedFaculty,
		subject: selectedSubject,
		page: page.current
	}

	if (number != null)
		data.number = number
	if (repeat != null)
		data.repeat = repeat
	if (countgpa != null)
		data.countgpa = countgpa

	if (!ignorePrev && JSON.stringify(data) == JSON.stringify(prevData))
		return

	prevData = data

	$(".loading").show()
	$(".loaded").hide()

	$.ajax({
		url: "/api/courses",
		method: "GET",
		data: data,
		traditional: true,
		success: (response) => {callback(response)},
		error: (response) => {
			$(".loading").hide()
			displayError(response)
		}
	})
}

function toggleCourseTag(courseId, tagId) {
	$.ajax({
		url: "/api/tags/" + tagId +"/course/" + courseId,
		method: "PUT",
		success: (data) => {
			alert("success", data.success)
			updateCourseTags(courseId)
		},
		error: (data) => {
			displayError(data)
		}
	})
}

function addCollection(courseId, collectionId) {
	$.ajax({
		url: "/api/users/course",
		method: "POST",
		data: {
			course_id: courseId,
			collection_id: collectionId
		},
		success: (data) => {
			prevData = {}
			requestResults((data) => {
				updateResults(data)
			})
		},
		error: (data) => {
			displayError(data)
		}
	})
}

//
// UPDATE FUNCS
//

function updateSubjects() {
	var subjSearch = $("#subjectSearch").val().toUpperCase()
	$("#subjectSearch").val("")

	if (subjSearch in subjects)
		subjects[subjSearch].sel = true

	$("#subjectSelector").empty()

	for (let s in subjects) {
		if (subjects[s].sel) {
			$("#subjectSelector").append(`
				<span class="badge btn btn-secondary border-secondary px-1 py-1 m-1 ms-0 font-monospace text-light fs-6 fw-normal subjItem" code="` + s + `"  title="Click to remove">
					` + s + `
				</span>
			`)
		}
	}
}

function updateCourseTags(courseId) {
	const item = $("#course-" + courseId)
	let icon = ""
	requestCourseTags(
		courseId,
		(response) => {
			item.find(".tags-dropdown").children(".tags-dropdown-item").each(function () {
				$(this).find(".bi-check").addClass("invisible")
			})

			const container = item.find(".tags-selected")
			container.empty()
			for (tag of response.tags) {

				if (tag.emoji)
					icon = "&#" + tag.emoji + " "
				else
					icon = "<i class='bi-circle-fill' style='color: #" + tag.color_hex +";'></i> "

				container.append(`
					<span class="course-tag btn badge btn-secondary px-1" title="`+ tag.name + `" style="cursor: pointer;" db-id="` + tag.id + `" onclick="toggleCourseTag(` + item.attr("db-id") + `, ` +  tag.id+ `)">
						` + icon + tag.name + `
					</span>
				`)

				item.find(".tags-dropdown").children(".tags-dropdown-item").each(function () {
					if($(this).attr("db-id") == tag.id)
						$(this).find(".bi-check").removeClass("invisible")
				})
			}
		}
	)
}

function updateResults(data) {
	$(".loading").hide()
	$(".loaded").show()

	$("#coursesContainer").empty()
	for (let course of data.results) {
		let courseItem = $("#templates .course-item").clone()

		courseItem.attr("id", "course-" + course.id)
		courseItem.attr("db-id", course.id)

		courseItem.find(".course-link").attr("href", course.url)
		courseItem.find(".course-emoji").html("&#" + (course.emoji ? course.emoji : DEFAULT_EMOJI))
		courseItem.find(".course-code").text(course.code)
		courseItem.find(".course-name").text(course.name)

		// Add content only available if user is authenticated
		if (isAuth) {
			// Add course collections

			const collections = courseItem.find(".course-collections")

			let message = ""
			if (course.collections.length == 0)
				message = "Not taken"
			else if (course.collections.length == 1)
				message = "Taken in " + course.collections.length + " term"
			else
				message = "Taken in " + course.collections.length + " terms"

			collections.find(".collections-dropdown-btn").text(message)

			const dropdown = collections.find(".collections-dropdown")

			dropdown.children(".collections-dropdown-item").each(function () {
				$(this).find(".dropdown-item").attr("onclick", "addCollection('" + course.id + "', '" + $(this).attr("db-id") + "')")
				$(this).find(".bi-check").addClass("invisible")
			})

			for (let collection of course.collections) {
				dropdown.children(".collections-dropdown-item").each(function () {
					if ($(this).attr("db-id") == collection.id) {
						$(this).find(".dropdown-item").attr("onclick", "")
						$(this).find(".bi-check").removeClass("invisible")
					}
				})
			}

			// Add tag badges
			var icon = ""
			for (let id of course.tags) {
				var tag = null

				for (t of userTags) {
					if (t.id == id) {
						tag = t
						break
					}
				}
				
				if (!tag)
					continue

				if (tag.emoji)
					icon = "&#" + tag.emoji + " "
				else
					icon = "<i class='bi-circle-fill' style='color: #" + tag.color_hex + ";'></i> "

				courseItem.find(".tags-selected").append(`
					<span class="course-tag btn badge btn-secondary px-1" style="cursor: pointer;" db-id="` + tag.id + `" onclick="toggleCourseTag(` + course.id + `, ` +  tag.id+ `)" title="Click to remove tag">
						` + icon + tag.name + `
					</span>
				`)
			}

			// Add tag dropdown items to tag dropdown
			for (let tag of userTags) {
				courseItem.find(".tags-dropdown").append(`
					<li class="tags-dropdown-item" db-id="` + tag.id +`">
						<a class="dropdown-item px-2 py-1" onclick="toggleCourseTag(` + course.id + `, ` +  tag.id + `)" style="cursor: pointer;">
							<i class="bi-check ` + (course.tags.includes(tag.id) ? `` : `invisible`) + `"></i>
							<small>` + tag.name +`</small>
						</a>
					</li>
				`)
			}

			courseItem.find(".tags-dropdown").append(`
				<li><hr class="dropdown-divider my-1"></li>
				<li><a class="dropdown-item px-2 p-y1" href="" data-bs-toggle="modal" data-bs-target="#modalEditTags">
					<i class="bi-pencil-square"></i>
					<small>Edit tags</small>
				</a></li>
			`)
		}

		courseItem.appendTo("#coursesContainer")
	}

	$(".num-total").text(data.total)

	page.current = data.page
	page.total = data.pages

	page.updateNav()
}

//
// EVENTS
//

$(document).on("click", ".subjItem", function () {
	subjects[this.getAttribute("code")].sel = false
	this.remove()
	$("#formFilterCourses").submit()
});

$(document).on("click", ".subjSuggestion", function () {
	$("#subjectSearch").val(this.getAttribute("code"))
	$("#subjectSearchSuggestions").empty()
	$("#formFilterCourses").submit()
});

$(document).on("click", ".tags-dropdown-btn", function(e) {
	if (!isAuth) {
		e.preventDefault()
		alert("warning", "You must be logged in to add tags")
	}
})

//
// DOCUMENT READY
//

$(document).ready(() => {
	if (isAuth) {
		tagsInit(() => {
			requestResults((data) => {
				updateResults(data)
			}, true)
		})
	} else {
		page.callback()
	}

	updateSubjects()

	$("#subjectSearch").keyup((e) => {
		$("#subjectSearchSuggestions").empty()
		if (e.keyCode == 13) {
			$("#subjectSearch").dropdown("hide")
			$("#formFilterCourses").submit()
			$("#subjectSearch").dropdown("show")
		} else {
			var subjSearch = $("#subjectSearch").val().toUpperCase()
			if (subjSearch.length > 0) {
				for (s in subjects) {
					if (s.startsWith(subjSearch)) {
						$("#subjectSearchSuggestions").append(`
							<li><a class="subjSuggestion dropdown-item form-control-sm px-2 py-1" href="#" code="` + s +`"><span class="font-monospace">` +
							s + `</span> - ` + subjects[s].name +
							`</a></li>
						`)
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

		// Remove query parameters
		window.history.pushState({}, document.title, window.location.pathname)

		// Switch page and request and update data
		page.switch(1)
	})
})
