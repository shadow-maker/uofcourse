function updateResults(data) {
	$("#subjectSelector").empty()
	for (let s in subjects) {
		if (subjects[s].sel) {
			$("#subjectSelector").append(`
				<span class="bg-secondary px-2 py-1 m-1 rounded mono-font text-light subjItem" id="subj` + s + `" onclick="remSubj('` + s + `')">` + s + `</span>
			`)
		}
	}

	$("#coursesContainer").empty()
	for (let course of data.courses) {
		$("#coursesContainer").append(`
			<div class="course-item card mb-3 bg-light">
				<div class="card-body row px-4 py-2">
					<a class="col-10 h5 p-0 m-0 text-black" href="/c/` + course.subj + `/` + course.code + `" style="text-decoration: none;">
						<span class="p-0 m-0">&#` + course.emoji + `</span>
						<span class="p-0 m-0 me-md-4 me-2 mono-font card-title">` + course.subj + `-` + course.code + `</span>
						<span class="p-0 m-0">` + course.name + `</span>
					</a>
					<div class="col-2 course-actions">
						&#11088
					</div>
				</div>
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



function requestResults(after) {
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
		else if (s.toUpperCase() == $("#subjectSearch").val().toUpperCase()) {
			subjects[s].sel = true
			selectedSubject.push(parseInt(subjects[s].id))
		}
	}

	$("#subjectSearch").val("")

	$.ajax({
		data: {
			sort: $("#sortBy").val(),
			order: $("#orderBy").val(),
			levels: JSON.stringify(selectedLevel),
			faculties: JSON.stringify(selectedFaculty),
			subjects: JSON.stringify(selectedSubject),
			page: page
		},
		type: "GET",
		url: "/api/c/filter",
	}).done(function (data) {
		after(data)
	})
}



$(document).ready(function () {
	$("#errorPopup").hide();

	requestResults(function (data) {
		if (data.error) {
			$("#errorPopup").show();
			$("#errorPopup .message").text(data.error);
		} else {
			page = data.page
			pages = data.pages
			updateResults(data)
		}
	})

	//$("#subjectSearch").keyup(function () {
	//	console.log($("#subjectSearch").val());
	//})

	$("form").on("submit", function (event) {
		event.preventDefault()
		event.stopImmediatePropagation()

		requestResults(function (data) {
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