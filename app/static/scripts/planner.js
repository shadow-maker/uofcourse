//
// GLOBAL VARS
//

var oldContainer = null

const modalInfo = $("#modalInfoUserCourse")
const formAdd = $("#formAddUserCourse")
const formEdit = $("#formEditUserCourse")

//
// UTIL FUNCS
//

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

function transferredShow() {
	putTransferred(true, () => {
		$(".transfer").show()
		$(".transfer-collapsed").hide()	
	})
}

function transferredHide() {
	putTransferred(false, () => {
		$(".transfer").hide()
		$(".transfer-collapsed").show()
		$(".transfer").find(".countInGPA").prop("checked", false)
		updateOverallGPA()
	})
}

// Check course funcs for add modal

function selectCourseStatus(status) {
	$("#selectCourseStatus").children("span").hide()
	if (status)
		$("#selectCourseStatus ." + status).show()
}

function checkCourse() {
	getCourseExists($("#selectCourseSubject").val(), $("#selectCourseNumber").val(), (exists, id) => {
		if (exists) {
			$("#selectCourseId").val(id)
			$("#selectCourseSubmit").prop("disabled", false)
			selectCourseStatus("success")
		} else {
			$("#selectCourseId").val("")
			$("#selectCourseSubmit").prop("disabled", true)
			selectCourseStatus("error")
		}
	})
}

//
// REQUEST FUNCS
//

function getCourseExists(subject, number, callback) {
	$.ajax({
		url: "/api/courses/code/" + subject + "/" + number,
		method: "GET",
		success: (response) => {
			callback(true, response.id)
		},
		error: (response) => {
			callback(false, null)
		}
	})
}

function getCollectionGPA(id, callback) {
	$.ajax({
		url: "/api/users/collection/" + id + "/gpa",
		method: "GET",
		success: (response) => {
			callback(response)
		},
		error: (response) => {
			displayError(response)
		}
	})
}

function putTransferred(set, callback) {
	$.ajax({
		url: "/api/users/session/transferred",
		method: "PUT",
		data: {set: set},
		success: (response) => {
			callback(response)
		},
		error: (response) => {
			displayError(response)
		}
	})
}

function putCollection(data, callback) {
	$.ajax({
		url: "/api/users/course",
		method: "PUT",
		data: data,
		success: (response) => {
			callback(response)
		},
		error: (response) => {
			displayError(response)
		}
	})
}

//
// UPDATE FUNCS
//

function updateSelectPassed() {
	if (formEdit.find("#selectPassed").prop("checked")) {
		formEdit.find("#selectPassedTrue").prop("checked", true)
		formEdit.find("#selectPassedFalse").prop("checked", false)
	} else {
		formEdit.find("#selectPassedTrue").prop("checked", false)
		formEdit.find("#selectPassedFalse").prop("checked", true)
	}
}

function updateCollectionsGPA() {
	$("#collectionsContainer").children(".collection-item").each(function () {
		getCollectionGPA($(this).attr("db-id"), (data) => {
			const gpaElem = $(this).find(".collection-gpa")
	
			if (data.gpa) {
				$(this).attr("db-units", data.units)
				$(this).attr("db-points", data.points)
				$(this).attr("db-gpa", data.gpa)
				gpaElem.find(".gpa").text(data.gpa)
				gpaElem.find(".gpa").attr(
					"data-bs-original-title",
					data.gpa + " x " + data.units + " = " + data.points + " points"
				)
				gpaElem.find(".nogpa").addClass("d-none")
				$(this).find(".countInGPA").prop("checked", true)
				$(this).find(".countInGPA").prop("disabled", false)
			} else {
				gpaElem.find(".gpa").text("")
				gpaElem.find(".nogpa").removeClass("d-none")
				$(this).find(".countInGPA").prop("checked", false)
				$(this).find(".countInGPA").prop("disabled", true)
			}

			updateOverallGPA()
		})
	})
}

function updateOverallGPA() {
	let sumUnits = 0
	let sumPoints = 0
	const overall = $("#overallGPA")
	overall.find("#overallCollectionContainer").empty()

	$("#collectionsContainer").children(".collection-item").each(function () {
		if ($(this).find(".countInGPA").prop("checked")) {
			sumUnits += parseFloat($(this).attr("db-units"))
			sumPoints += parseFloat($(this).attr("db-points"))

			let overallCollection = `
			<div class="row overall-collection-item">
				<span class="col-12 col-sm-3 text-sm-end ps-sm-2 fw-bold">
					` + $(this).attr("db-term") +`
				</span>
				<span class="col-6 col-sm-4 font-monospace pe-0">
					<span class="d-inline-block" style="width: 3.1em;" title="Term GPA">
						` + $(this).attr("db-gpa") +`
					</span>
					x
					<span class="d-inline-block" style="width: 2.9em;" title="Term accumulated units">
						` + $(this).attr("db-units") +`
					</span>
					=
				</span>
				<span class="col-2 font-monospace px-0 d-flex justify-content-between" title="Term accumulated points">
					<span>` + $(this).attr("db-points") +`</span>
					<i class="disable bi-x pe-sm-2" title="Hide in overall GPA" onclick="disableOverallGPA('` + $(this).attr("db-id") +`')"></i>
				</span>
			</div>`
			overall.find("#overallCollectionContainer").append(overallCollection)
		}
	})

	overall.find(".sum-points").text(Number((sumPoints).toFixed(3)))
	overall.find(".sum-units").text(sumUnits)
	overall.find(".final-gpa").text(sumUnits ? Number((sumPoints / sumUnits).toFixed(3)) : "-")
}

function disableOverallGPA(collectionId) {
	$("#collectionsContainer").children(".collection-item").each(function () {
		if ($(this).attr("db-id") == collectionId) {
			$(this).find(".countInGPA").prop("checked", false)
			updateOverallGPA()
		}
	})
}

//
// DRAG EVENT LISTENERS
//

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
			putCollection({
				id: item.getAttribute("db-id"),
				collection_id: item.parentElement.getAttribute("db-id")
			}, updateCollectionsGPA)
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

//
// EVENTS
//

// Set collection.id input in formAdd whenever its opened
$(document).on("click", ".add-course", function() {
	formAdd.find("#selectCollectionId").val(this.getAttribute("db-id"))
})

// On modal starts to show
$("#modalAddCourse").on("show.bs.modal", () => {
	// Clear form inputs
	formAdd.find(".selectSubject").val("")
	formAdd.find(".selectNumber").val("")
	
	// Hide status and feedback
	formAdd.find("#selectCourseStatus").children("span").hide()
	formAdd.find(".feedback").addClass("invisible")

	// Disable submit button
	formAdd.find(".submit").prop("disabled", true)
})

// On modal is shown
$("#modalAddCourse").on("shown.bs.modal", () => {
	// Move focus to subject selection when modal is shown
	formAdd.find(".selectSubject").focus()
})

// On key up inside subject selection
$("#selectCourseSubject").on("keyup", function(e) {
	// Convert subject into uppercase
	$(this).val($(this).val().toUpperCase())

	// Remove numeric characters
	$(this).val($(this).val().replace(/[0-9]/g, ""))

	if ($(this).val().length < $(this).attr("minLength")) {
		formAdd.find(".selectNumber").prop("disabled", true)
		formAdd.find(".submit").prop("disabled", true)
		formAdd.find(".feedback").addClass("invisible")
		selectCourseStatus("")
	} else {
		formAdd.find(".selectNumber").prop("disabled", false)
		if (formAdd.find(".selectNumber").val().length == formAdd.find(".selectNumber").attr("maxLength"))
			checkCourse()
	}

	// Move focus to number selection if max length is reached
	if ($(this).val().length == $(this).attr("maxLength"))
		formAdd.find(".selectNumber").focus()
})

// On key up inside number selection
$("#selectCourseNumber").on("keydown", function(e) {
	// If pressing backspace and the value is empty, move focus to subject selection
	if ($(this).val().length == 0 && e.keyCode == 8)
		formAdd.find(".selectSubject").focus()
	else if (e.keyCode == 13)
		formAdd.submit()
})

// On key down inside number selection
$("#selectCourseNumber").on("keyup", function(e) {
	// Remove non-numeric characters
	$(this).val($(this).val().replace(/\D/g, ""))

	// Check course if length is complete
	if ($(this).val().length == $(this).attr("maxLength")) {
		checkCourse()
	} else {
		formAdd.find(".submit").prop("disabled", true)
		formAdd.find(".feedback").addClass("invisible")
		selectCourseStatus("")
	}
})

// UserCourse click
$(document).on("click", ".collection-course-item", function() {
	if (!this.classList.contains("dragging")) {
		let gradeId = this.getAttribute("db-grade")
		if (gradeId) {
			const grade = grades[gradeId]
			modalInfo.find(".grade-symbol").text(grade.symbol)
			modalInfo.find(".grade-desc").text(grade.desc)
			modalInfo.find(".grade-passed").text(grade.passed ? "Yes" : "No")
			if (grade.gpv) {
				modalInfo.find(".grade-gpv").text(grade.gpv)
				modalInfo.find(".grade-weighted").text(
					Number((grade.gpv * parseFloat(this.getAttribute("db-units"))).toFixed(3))
				)
			} else {
				modalInfo.find(".grade-gpv").text("N/A")
				modalInfo.find(".grade-weighted").text("N/A")
			}
		} else {
			modalInfo.find(".grade-symbol").text("-")
			modalInfo.find(".grade-desc").text("")
			modalInfo.find(".grade-gpv").text("")
			modalInfo.find(".grade-passed").text("")
			modalInfo.find(".grade-weighted").text("")
			gradeId = "0"
		}
		let passed = this.getAttribute("db-passed")
		let collectionId = this.parentElement.getAttribute("db-id")

		modalInfo.find(".term").text(this.getAttribute("db-term"))
		modalInfo.find(".link").prop("href", this.getAttribute("db-url"))
		modalInfo.find(".emoji").text($(this).find(".emoji").text())
		modalInfo.find(".code").text(this.getAttribute("db-code"))
		modalInfo.find(".name").text(this.getAttribute("db-name"))
		modalInfo.find(".units").text(this.getAttribute("db-units"))
		modalInfo.find(".repeat").text(this.getAttribute("db-repeat") == "true" ? "Yes" : "No")
		modalInfo.find(".countgpa").text(this.getAttribute("db-countgpa") == "true" ? "Yes" : "No")

		formEdit.find("#selectCourse").val(this.getAttribute("db-id"))
		formEdit.find("#selectCoursePlaceholder").val(this.getAttribute("db-code"))
		formEdit.find("#selectCollection").val(collectionId)
		formEdit.find("#selectGrade").val(gradeId)

		if (passed == "true") {
			formEdit.find("#selectPassed").prop("checked", true)
			formEdit.find("#selectPassedTrue").prop("checked", true)
			formEdit.find("#selectPassedFalse").prop("checked", false)
		} else if (passed == "false") {
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

//
// DOCUMENT READY
//

$(document).ready(() => {
	transferredShow()

	updateCollectionsGPA()

	if (showTransferred)
		transferredShow()
	else
		transferredHide()

	$("#formEditUserCourse #selectGrade").change(function() {
		$("#formEditUserCourse #selectPassed").prop("checked",
			grades[$(this).val()] ? grades[$(this).val()].passed : false
		)
		updateSelectPassed()
	})

	$("#formEditUserCourse #selectPassed").change(updateSelectPassed)
	$(".collection-item .countInGPA").change(updateOverallGPA)
})
