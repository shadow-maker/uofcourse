var oldContainer = null

function sortCourses(container) {
	$(container).children(".collection-course-item").sort(function (a, b) {
		if (($(a).attr("db-code").toLowerCase() > $(b).attr("db-code").toLowerCase()) )
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

// Dragging

const courseContainers = document.querySelectorAll(".collection-course-container")
const courseItems = document.querySelectorAll(".collection-course-item")

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

			if (response.gpa) {
				gpaElem.find(".gpa").text(response.gpa)
				gpaElem.find(".nogpa").addClass("d-none")
			} else {
				gpaElem.find(".gpa").text("")
				gpaElem.find(".nogpa").removeClass("d-none")
			}
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

function getGrade(id, callback) {
	$.ajax({
		url: "/api/grades/" + id,
		method: "GET",
		success: (response) => {
			callback(response)
		},
		error: (response) => {
			displayError(response)
		}
	})
}

$(document).on("click", ".collection-course-item", function() {
	if (!this.classList.contains("dragging")) {
		let modalInfo = $("#modalInfoUserCourse")
		let formEdit = $("#formEditUserCourse")

		let courseId = this.getAttribute("db-id")
		let term = this.getAttribute("db-term")
		let courseCode = this.getAttribute("db-code")
		let courseName = this.getAttribute("db-name")
		let courseNogpa = this.getAttribute("db-nogpa")
		let courseURL = this.getAttribute("db-url")
		let courseGrade = this.getAttribute("db-grade")
		if (courseGrade) {
			getGrade(courseGrade, (data) => {
				modalInfo.find(".grade-symbol").text(data.symbol)
				modalInfo.find(".grade-desc").text(data.desc)
				modalInfo.find(".grade-gpv").text(data.gpv)
				modalInfo.find(".grade-passed").text(data.passed ? "Yes" : "No")
			})
		} else {
			modalInfo.find(".grade-symbol").text("-")
			modalInfo.find(".grade-desc").text("")
			modalInfo.find(".grade-gpv").text("")
			modalInfo.find(".grade-passed").text("")
			courseGrade = "0"
		}
		let coursePassed = this.getAttribute("db-passed")
		let collectionId = this.parentElement.getAttribute("db-id")

		modalInfo.find(".term").text(term)
		modalInfo.find(".link").prop("href", courseURL)
		modalInfo.find(".code").text(courseCode)
		modalInfo.find(".name").text(courseName)
		modalInfo.find(".countgpa").text(courseNogpa == "True" ? "No" : "Yes")

		formEdit.find("#selectCourse").val(courseId)
		formEdit.find("#selectCoursePlaceholder").val(courseCode)
		formEdit.find("#selectCollection").val(collectionId)
		formEdit.find("#selectGrade").val(courseGrade)

		if (coursePassed == "true") {
			formEdit.find("#selectPassed").prop("checked", true)
			formEdit.find("#selectPassedTrue").prop("checked", true)
			formEdit.find("#selectPassedFalse").prop("checked", false)
		} else if (coursePassed == "true") {
			formEdit.find("#selectPassed").prop("checked", false)
			formEdit.find("#selectPassedTrue").prop("checked", false)
			formEdit.find("#selectPassedFalse").prop("checked", true)
		} else {
			formEdit.find("#selectPassed").prop("checked", false)
			formEdit.find("#selectPassedTrue").prop("checked", false)
			formEdit.find("#selectPassedFalse").prop("checked", false)
		}
	}
})

function updateSelectPassed() {
	let form = $("#formEditUserCourse")
	if (form.find("#selectPassed").prop("checked")) {
		form.find("#selectPassedTrue").prop("checked", true)
		form.find("#selectPassedFalse").prop("checked", false)
	} else {
		form.find("#selectPassedTrue").prop("checked", false)
		form.find("#selectPassedFalse").prop("checked", true)
	}
}

//
// DOCUMENT READY
//

$(document).ready(() => {
	tagsInit()

	$("#formEditUserCourse #selectGrade").change(function() {
		$("#formEditUserCourse #selectPassed").prop("checked",
			grades[$(this).val()] ? grades[$(this).val()].passed : false
		)
		updateSelectPassed()
	})

	$("#formEditUserCourse #selectPassed").change(updateSelectPassed)
})
