function displayError(data) {
	if (data.error)
		alert("danger", data.error)
	else
		alert("danger", data.responseJSON.error)
}

var prevData = {}

//
// REQUEST FUNCTIONS
//

function requestResults(suc, ignorePrev=false) {
	var selectedLevel = []
	$("input[name='selectedLevel']:checked").each(function () {
		selectedLevel.push(parseInt($(this).val()))
	})

	var selectedFaculty = []
	$("input[name='selectedFaculty']:checked").each(function () {
		selectedFaculty.push(parseInt($(this).val()))
	})

	var selectedSubject = []
	for (let s in subjects)
		if (subjects[s].sel)
			selectedSubject.push(parseInt(subjects[s].id))

	var data = {
		sort: $("#sortBy").val(),
		asc: $("#orderBy").val(),
		levels: JSON.stringify(selectedLevel),
		faculties: JSON.stringify(selectedFaculty),
		subjects: JSON.stringify(selectedSubject),
		page: page
	}

	if (!ignorePrev && JSON.stringify(data) == JSON.stringify(prevData)) {
		return
	}

	prevData = data

	$(".loading").show()
	$(".loaded").hide()

	$.ajax({
		url: "/api/courses/filter",
		method: "GET",
		data: data,
		success: (data) => {suc(data)},
		error: (data) => {
			$(".loading").hide()
			displayError(data)
		}
	})
}


function requestCourseTags(id, suc) {
	if (isAuth)
		$.ajax({
			url: "/api/tags/course/" + id,
			method: "GET",
			success: (data) => {suc(data)},
			error: (data) => {
				displayError(data)
			}
		})
}

function toggleTag(courseId, tagId) {
	$.ajax({
		url: "/api/tags/course",
		method: "PUT",
		data: {
			course_id: courseId,
			tag_id: tagId
		},
		success: (data) => {
			alert("success", data.success)
			updateCourseTags(courseId)
		},
		error: (data) => {
			displayError(data)
		}
	})
}

//
// UPDATE FUNCTIONS
//

function updateCourseTags(courseId) {
	let item = $("#course-" + courseId)
	var icon = ""
	requestCourseTags(
		courseId,
		(data) => {
			item.find(".tags-dropdown").children(".tags-dropdown-item").each(function () {
				$(this).find(".bi-check").addClass("invisible")
			})

			const container = item.find(".tags-selected")
			container.empty()
			for (tag of data.tags) {

				if (tag.emoji)
					icon = "&#" + tag.emoji + " "
				else
					icon = "<i class='bi-circle-fill' style='color: #" + tag.color_hex +";'></i> "

				container.append(`
					<span class="course-tag btn badge btn-secondary px-1" title="`+ tag.name + `" style="cursor: pointer;" db-id="` + tag.id + `" onclick="toggleTag(` + item.attr("db-id") + `, ` +  tag.id+ `)">
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
		var courseItem = $("#templateCourseItem").children().first().clone()

		courseItem.attr("id", "course-" + course.id)
		courseItem.attr("db-id", course.id)

		courseItem.find(".course-link").attr("href", course.url)
		courseItem.find(".course-emoji").html("&#" + course.emoji)
		courseItem.find(".course-code").html(course.code_full)
		courseItem.find(".course-name").html(course.name)


		var icon = ""
		for (let id of course.tags) {
			var tag = null

			for (t of userTags)
				if (t.id == id)
					tag = t
			
			if (!tag)
				continue

			if (tag.emoji)
				icon = "&#" + tag.emoji + " "
			else
				icon = "<i class='bi-circle-fill' style='color: #" + tag.color_hex + ";'></i> "

			courseItem.find(".tags-selected").append(`
				<span class="course-tag btn badge btn-secondary px-1" title="`+ tag.name + `" style="cursor: pointer;" db-id="` + tag.id + `" onclick="toggleTag(` + course.id + `, ` +  tag.id+ `)">
					` + icon + tag.name + `
				</span>
			`)
		}

		if (isAuth) {
			for (tag of userTags) {
				courseItem.find(".tags-dropdown").append(`
					<li class="tags-dropdown-item" db-id="` + tag.id +`">
						<a class="dropdown-item px-2 py-1" onclick="toggleTag(` + course.id + `, ` +  tag.id + `)" style="cursor: pointer;">
							<small>
								<i class="bi-check ` + (course.tags.includes(tag.id) ? `` : `invisible`) + `"></i>
								` + tag.name +`
							</small>
						</a>
					</li>
				`)
			}

			courseItem.find(".tags-dropdown").append(`
				<li><hr class="dropdown-divider my-1"></li>
				<li><a class="dropdown-item px-2 p-y1" href="" data-bs-toggle="modal" data-bs-target="#modalEditTags" onclick="loadEditTagsModal()">
					<small>Edit tags</small>
				</a></li>
			`)
		}

		courseItem.appendTo("#coursesContainer")
	}

	$("#pageNav .pageSelector").remove()
	if (pages > 15) {
		$("#pageNav .pageEllipsis").show()
	} else {
		$("#pageNav .pageEllipsis").hide()
		for (let p = pages; p > 0; p--) {
			$("#pageNav ul li:eq(0)").after(`
				<li class="pageSelector page-item ` + ((p == page) ? `active` : ``) + `"
				onclick="switchPage(` + ((p == page) ? -1 : p) + `)" style="cursor: pointer;">
					<a class="page-link">` + p +`</a>
				</li>
			`)
		}
	}

	$("#numTotal").text(data.total)
	$("#numPage").text(data.page)
	$("#numPages").text(data.pages)
}

//
// DOCUMENT READY
//

$(document).ready(() => {
	$("#formFilterCourses input").not("#subjectSearch").change(() => {
		$("#formFilterCourses").submit()
	})

	$("#formFilterCourses select").change(() => {
		$("#formFilterCourses").submit()
	})

	$("#formFilterCourses").on("submit", (event) => {
		event.preventDefault()
		event.stopImmediatePropagation()

		updateSubjects()

		requestResults((data) => {
			page = data.page
			pages = data.pages
			updateResults(data)
		})
	})
})

$(document).on("click", ".tags-dropdown-btn", function() {
	if (!isAuth)
		alert("warning", "You must be logged in to add tags")
})

function tagsInit() {
	requestResults((data) => {
		page = data.page
		pages = data.pages
		updateResults(data)
	})
}

function tagEditDone() {
	requestResults((data) => {
		page = data.page
		pages = data.pages
		updateResults(data)
	}, true)
}
