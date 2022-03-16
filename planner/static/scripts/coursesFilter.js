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
			alert("danger", data.responseJSON.error)
		}
	})
}


function requestUserTags(suc) {
	if (isAuth)
		$.ajax({
			url: "/api/tags",
			method: "GET",
			success: (data) => {suc(data)},
			error: (data) => {
				alert("danger", data.responseJSON.error)
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
				alert("danger", data.responseJSON.error)
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
			updateTags($("#course-" + courseId))
		},
		error: (data) => {
			alert("danger", data.error)
		}
	})
}

//
// UPDATE FUNCTIONS
//

function updateTags(item) {
	var emoji = ""
	var color = ""
	requestCourseTags(
		item.attr("db-id"),
		(data) => {
			item.find(".tags-dropdown").children(".tags-dropdown-item").each(function () {
				$(this).find(".bi-check").addClass("invisible")
			})

			const container = item.find(".tags-selected")
			container.empty()
			for (tag of data.tags) {
				emoji = ""
				if (tag.emoji)
					emoji = "&#" + tag.emoji + " "
				color = ("000000" + tag.color.toString(16)).slice(-6)

				container.append(`
					<span class="course-tag btn badge btn-secondary px-1" title="`+ tag.name + `" style="cursor: pointer; border-color: #` + color +`;" db-id="` + tag.id + `" onclick="toggleTag(` + item.attr("db-id") + `, ` +  tag.id+ `)">
						` + emoji + tag.name + `
					</span>
				`)

				item.find(".tags-dropdown").children(".tags-dropdown-item").each(function () {
					if($(this).attr("db-id") == tag.id) {
						$(this).find(".bi-check").removeClass("invisible")
					}
				})
			}
		}
	)
}

function updateResults(data) {
	$(".loading").hide()
	$(".loaded").show()


	function tagsUser(courseId) {
		var html = ""

		for (let id in userTags) {
			html += `
				<li class="tags-dropdown-item" db-id="` + id +`">
					<a class="dropdown-item px-2 py-1" onclick="toggleTag(` + courseId + `, ` +  id + `)" style="cursor: pointer;">
						<small>
							<i class="bi-check invisible"></i>
							` + userTags[id].name +`
						</small>
					</a>
				</li>
			`
		}

		return html
	}

	$("#coursesContainer").empty()
	for (let course of data.results) {
		$("#coursesContainer").append(`
			<div class="course-item card mb-3 bg-light" id="course-` + course.id + `" db-id="` + course.id + `">
				<div class="card-body row px-4 pt-0 pb-2">
					<div class="col-10 p-0 m-0">
						<a class="row m-0 p-0 pt-2 text-decoration-none text-body" href="/c/` + course.subj + `/` + course.code + `">
							<div class="h4 m-0 d-flex align-items-bottom col-xl-3 col-lg-4 col-12">
								<span class="p-0 m-0 me-2">&#` + course.emoji + `</span>
								<span class="p-0 m-0 font-monospace">` + course.subj + `-` + course.code + `</span>
							</div>
							<div class="d-flex align-items-bottom col-xl-9 col-lg-8 col-12">
								<div class="p-0 m-0 h5">` + course.name + `</div>
							</div>
						</a>
						<div class="row m-0 p-0">
							<div class="h4 m-0 col-xl-3 col-lg-4 col-12"></div>
							<div class="col-xl-9 col-lg-8 col-12">
								<span class="tags-selected p-0 m-0"></span>
								<div class="btn-group">
									<button class="tags-dropdown-btn btn btn-secondary btn-sm badge dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">
										<i class="bi-tag-fill"></i>
									</button>
									<ul class="tags-dropdown dropdown-menu fs-6 py-1">
									` + (isAuth ?
										tagsUser(course.id) + `
										<li><hr class="dropdown-divider my-1"></li>
										<li><a class="dropdown-item px-2 p-y1" href="" data-bs-toggle="modal" data-bs-target="#modalEditTags">
											<small>Edit tags</small>
										</a></li>
									` : ``) + `
									</ul>
								</div>
							</div>
						</div>	
					</div>
					<div class="col-2 course-actions">
						Taken in
					</div>
				</div>
			</div>
		`)
		updateTags($("#coursesContainer").children().last())
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
	requestResults(
		(data) => {
			page = data.page
			pages = data.pages
			updateResults(data)
		}
	)

	$("input").not("#subjectSearch").change(() => {
		$("#formFilterCourses").submit()
	})

	$("select").change(() => {
		$("#formFilterCourses").submit()
	})

	$("#formFilterCourses").on("submit", (event) => {
		event.preventDefault()
		event.stopImmediatePropagation()

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

function tagEditDone(after) {
	requestUserTags((data) => {
		userTags = data.tags
		after()
		requestResults((data) => {
			page = data.page
			pages = data.pages
			updateResults(data)
		}, true)
	})
}
