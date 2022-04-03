// Dragging

const courseContainers = document.querySelectorAll(".collection-course-container")
const courseItems = document.querySelectorAll(".collection-course-item")

var oldContainer = null

courseItems.forEach(item => {
	item.addEventListener("dragstart", () => {
		item.classList.add("dragging")
		oldContainer = item.parentElement
	})

	item.addEventListener("dragend", () => {
		item.classList.remove("dragging")

		if (oldContainer != item.parentElement) {
			editCollection({
				id: item.getAttribute("db-id"),
				collection_id: item.parentElement.getAttribute("db-id")
			}, [oldContainer, item.parentElement])
		}
	})
})

courseContainers.forEach(container => {
	container.addEventListener("dragover", e => {
		e.preventDefault()
		const item = document.querySelector(".dragging")
		container.appendChild(item)
		sortCourses(container)
	})
})

// AJAX for dragging course items

function updateCollectionGPA(container) {
	$.ajax({
		url: "/api/users/collection/" + container.getAttribute("db-id") + "/gpa",
		method: "GET",
		success: (response) => {
			const gpaElem = $(container.parentElement).children(".card-footer").children(".row").children(".collection-gpa")

			if (response.gpa)
				gpaElem.text(response.gpa)
			else
				gpaElem.text("-")
		},
		error: (response) => {
			displayError(response)
		}
	})
}

function editCollection(data, containers) {
	$.ajax({
		url: "/api/users/course",
		method: "PUT",
		data: data,
		success: () => {
			containers.forEach((container) => {
				updateCollectionGPA(container)
			})
		},
		error: (response) => {
			displayError(response)
		}
	})
}

function sortCourses(container) {
	$(container).children(".collection-course-item").sort(function (a, b) {
		if ( ($(a).attr("db-code").toLowerCase() > $(b).attr("db-code").toLowerCase()) )
			return 1
		else if (($(a).attr("db-code").toLowerCase() == $(b).attr("db-code").toLowerCase()))
			return 0
		else
			return -1
	}).each(function () {
		var elem = $(this)
		elem.remove()
		$(elem).appendTo(container)
	})
}


// UserCourse-add form logic

function selectCourseStatus(status) {
	$("#selectCourseStatus").children("span").hide()
	if (status)
		$("#selectCourseStatus ." + status).show()
}

function checkCourse() {
	//selectCourseStatus("loading")

	$.ajax({
		url: "/api/courses/code/" + $("#selectCourseSubject").val() + "/" + $("#selectCourseNumber").val(),
		method: "GET",
		success: (response) => {
			$("#selectCourseId").val(response.id)
			$("#selectCourseSubmit").prop("disabled", false)
			selectCourseStatus("success")
		},
		error: (response) => {
			$("#selectCourseId").val("")
			$("#selectCourseSubmit").prop("disabled", true)
			selectCourseStatus("error")
		}
	})
}

$("#selectCourseSubject").keyup(function() {
	if ($(this).val().length < $(this).attr("minLength")) {
		$("#selectCourseNumber").prop("disabled", true)
		$("#selectCourseSubmit").prop("disabled", true)
		selectCourseStatus("")
	} else {
		$("#selectCourseNumber").prop("disabled", false)
		if ($("#selectCourseNumber").val().length == $("#selectCourseNumber").attr("maxLength"))
			checkCourse()
	}

	if ($(this).val().length == $(this).attr("maxLength"))
		$("#selectCourseNumber").focus()
})

$("#selectCourseNumber").keyup(function() {
	if ($(this).val().length == $(this).attr("maxLength"))
		checkCourse()
	else
		$("#selectCourseSubmit").prop("disabled", true)
	selectCourseStatus("")
})

$(document).on("click", ".add-course", function() {
	$("#selectCollectionId").val(this.getAttribute("db-id"))
	$("#selectCourseSubject").focus()
})


// UserCourse-edit form logic

$(document).on("click", ".collection-course-item", function() {
	if (!this.classList.contains("dragging")) {
		let form = $("#formEditUserCourse")

		let courseId = this.getAttribute("db-id")
		let courseCode = this.querySelector("#code").innerText
		var courseGrade = this.getAttribute("db-grade")
		if (courseGrade == "")
			courseGrade = "0"
		let coursePassed = this.getAttribute("db-passed")
		let collectionId = this.parentElement.getAttribute("db-id")

		form.find("#selectCourse").val(courseId)
		form.find("#selectCoursePlaceholder").val(courseCode)
		form.find("#selectCollection").val(collectionId)
		form.find("#selectGrade").val(courseGrade)

		if (coursePassed == "true") {
			form.find("#selectPassedTrue").prop("checked", true)
			form.find("#selectPassedFalse").prop("checked", false)
		} else if (coursePassed == "false") {
			form.find("#selectPassedTrue").prop("checked", false)
			form.find("#selectPassedFalse").prop("checked", true)
		} else {
			form.find("#selectPassedTrue").prop("checked", false)
			form.find("#selectPassedFalse").prop("checked", false)
		}
	}
})
