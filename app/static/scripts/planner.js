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

function updateCollectionsGPA() {
	$("#collectionsContainer").children(".collection-item").each(function () {
		$.ajax({
			url: "/api/users/collection/" + $(this).attr("db-id") + "/gpa",
			method: "GET",
			success: (response) => {
				const gpaElem = $(this).find(".collection-gpa")
	
				if (response.gpa) {
					$(this).attr("db-units", response.units)
					$(this).attr("db-points", response.points)
					$(this).attr("db-gpa", response.gpa)
					gpaElem.find(".gpa").text(response.gpa)
					gpaElem.find(".gpa").attr(
						"data-bs-original-title",
						response.gpa + " x " + response.units + " = " + response.points + " points"
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
			},
			error: (response) => {
				displayError(response)
			}
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

function editCollection(data) {
	$.ajax({
		url: "/api/users/course",
		method: "PUT",
		data: data,
		success: () => {
			updateCollectionsGPA()
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

const selectCourse = $("#formAddCourse")

$(document).on("click", ".add-course", function() {
	selectCourse.find("#selectCollectionId").val(this.getAttribute("db-id"))
})

// On modal starts to show
$("#modalAddCourse").on("show.bs.modal", () => {
	// Clear form inputs
	selectCourse.find(".selectSubject").val("")
	selectCourse.find(".selectNumber").val("")
	
	// Hide status and feedback
	selectCourse.find("#selectCourseStatus").children("span").hide()
	selectCourse.find(".feedback").addClass("invisible")

	// Disable submit button
	selectCourse.find(".submit").prop("disabled", true)
})

// On modal is shown
$("#modalAddCourse").on("shown.bs.modal", () => {
	// Move focus to subject selection when modal is shown
	selectCourse.find(".selectSubject").focus()
})

// On key up inside subject selection
$("#selectCourseSubject").on("keyup", function(e) {
	// Convert subject into uppercase
	$(this).val($(this).val().toUpperCase())

	// Remove numeric characters
	$(this).val($(this).val().replace(/[0-9]/g, ""))

	if ($(this).val().length < $(this).attr("minLength")) {
		selectCourse.find(".selectNumber").prop("disabled", true)
		selectCourse.find(".submit").prop("disabled", true)
		selectCourse.find(".feedback").addClass("invisible")
		selectCourseStatus("")
	} else {
		selectCourse.find(".selectNumber").prop("disabled", false)
		if (selectCourse.find(".selectNumber").val().length == selectCourse.find(".selectNumber").attr("maxLength"))
			checkCourse()
	}

	// Move focus to number selection if max length is reached
	if ($(this).val().length == $(this).attr("maxLength"))
		selectCourse.find(".selectNumber").focus()
})

// On key up inside number selection
$("#selectCourseNumber").on("keydown", function(e) {
	// If pressing backspace and the value is empty, move focus to subject selection
	if ($(this).val().length == 0 && e.keyCode == 8)
		selectCourse.find(".selectSubject").focus()
	else if (e.keyCode == 13)
		selectCourse.submit()
})

// On key down inside number selection
$("#selectCourseNumber").on("keyup", function(e) {
	// Remove non-numeric characters
	$(this).val($(this).val().replace(/\D/g, ""))

	// Check course if length is complete
	if ($(this).val().length == $(this).attr("maxLength")) {
		checkCourse()
	} else {
		selectCourse.find(".submit").prop("disabled", true)
		selectCourse.find(".feedback").addClass("invisible")
		selectCourseStatus("")
	}
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

		let grade = this.getAttribute("db-grade")
		if (grade) {
			getGrade(grade, (data) => {
				modalInfo.find(".grade-symbol").text(data.symbol)
				modalInfo.find(".grade-desc").text(data.desc)
				modalInfo.find(".grade-passed").text(data.passed ? "Yes" : "No")
				if (data.gpv) {
					modalInfo.find(".grade-gpv").text(data.gpv)
					modalInfo.find(".grade-weighted").text(
						Number((data.gpv * parseFloat(this.getAttribute("db-units"))).toFixed(3))
					)
				} else {
					modalInfo.find(".grade-gpv").text("N/A")
					modalInfo.find(".grade-weighted").text("N/A")
				}
			})
		} else {
			modalInfo.find(".grade-symbol").text("-")
			modalInfo.find(".grade-desc").text("")
			modalInfo.find(".grade-gpv").text("")
			modalInfo.find(".grade-passed").text("")
			modalInfo.find(".grade-weighted").text("")
			grade = "0"
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
		formEdit.find("#selectGrade").val(grade)

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
	updateCollectionsGPA()

	$("#formEditUserCourse #selectGrade").change(function() {
		$("#formEditUserCourse #selectPassed").prop("checked",
			grades[$(this).val()] ? grades[$(this).val()].passed : false
		)
		updateSelectPassed()
	})

	$("#formEditUserCourse #selectPassed").change(updateSelectPassed)
	$(".collection-item .countInGPA").change(updateOverallGPA)
})
