var prevData = {}

function updateResults(data) {
	$(".loading").hide()
	$(".loaded").show()

	$("#coursesContainer").empty()
	for (let course of data.results) {
		$("#coursesContainer").append(`
			<div class="course-item card mb-3 bg-light">
				<a class="card-body row px-4 py-2 text-decoration-none" href="/c/` + course.subj + `/` + course.code + `">
					<div class="col-10 h5 p-0 m-0 text-black" style="text-decoration: none;">
						<span class="p-0 m-0">&#` + course.emoji + `</span>
						<span class="p-0 m-0 me-md-4 me-2 font-monospace card-title">` + course.subj + `-` + course.code + `</span>
						<span class="p-0 m-0">` + course.name + `</span>
					</div>
					<div class="col-2 course-actions">
						&#11088
					</div>
				</a>
			</div>
		`)
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



function requestResults(suc, err) {
	var selectedLevel = []
	$("input[name='selectedLevel']:checked").each(function () {
		selectedLevel.push(parseInt($(this).val()))
	})

	var selectedFaculty = []
	$("input[name='selectedFaculty']:checked").each(function () {
		selectedFaculty.push(parseInt($(this).val()))
	})

	var selectedSubject = []
	for (let s in subjects) {
		if (subjects[s].sel) {
			selectedSubject.push(parseInt(subjects[s].id))
		}
	}

	var data = {
		sort: $("#sortBy").val(),
		asc: $("#orderBy").val(),
		levels: JSON.stringify(selectedLevel),
		faculties: JSON.stringify(selectedFaculty),
		subjects: JSON.stringify(selectedSubject),
		page: page
	}

	if (JSON.stringify(data) == JSON.stringify(prevData)) {
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
		error: (data) => {err(data)}
	})
}



$(document).ready(() => {
	requestResults(
		(data) => {
			page = data.page
			pages = data.pages
			updateResults(data)
		},
		(data) => {
			$(".loading").hide()
			$("#errorPopup").show();
			$("#errorPopup .message").text(data.error);
		}
	)

	$("input").not("#subjectSearch").change(() => {
		$("form").submit()
	})

	$("select").change(() => {
		$("form").submit()
	})

	$("form").on("submit", (event) => {
		event.preventDefault()
		event.stopImmediatePropagation()

		updateSubjects()

		requestResults((data) => {
			if (data.error) {
				$("#errorPopup").show();
				$("#errorPopup .message").text(data.error);
			} else {
				page = data.page
				pages = data.pages
				updateResults(data)
			}
		})
	})
})