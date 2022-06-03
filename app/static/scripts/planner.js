//
// GLOBAL VARS
//

var collections = {}
var overallGPA = {
	sumUnits: 0,
	sumGPA: 0,
	finalGPA: 0
}

var oldContainer = null

const modalInfo = $("#modalInfoUserCourse")
const formAdd = $("#formAddUserCourse")
const formEdit = $("#formEditUserCourse")

//
// UTIL FUNCS
//

function sortCourses(container) {
	$(container).children(".collection-course-item").sort(function (a, b) {
		if (($(a).attr("db-code").toLowerCase() < $(b).attr("db-code").toLowerCase()))
			return -1
		else if (($(a).attr("db-code").toLowerCase() > $(b).attr("db-code").toLowerCase()))
			return 1
		else
			return 0
	}).each(function () {
		var elem = $(this)
		elem.remove()
		$(elem).appendTo(container)
	})
}

function transferredShow() {
	showTransferred = true
	putTransferred(true, () => {
		$(".transfer").removeClass("d-none")
		$("#transfer-collapsed").addClass("d-none")
	})
}

function transferredHide() {
	showTransferred = false
	putTransferred(false, () => {
		$(".transfer").addClass("d-none")
		$("#transfer-collapsed").removeClass("d-none")
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

// GET

function getCollections(callback) {
	$.ajax({
		url: "/api/me/collections",
		method: "GET",
		data: {
			sort: ["term_id"],
		},
		traditional: true,
		success: (response) => {
			callback(response)
		},
		error: (response) => {
			displayError(response)
		}
	})
}

function getCollection(id, callback) {
	$.ajax({
		url: "/api/me/collections/" + id,
		method: "GET",
		success: (response) => {
			callback(response)
		},
		error: (response) => {
			displayError(response)
		}
	})
}

function getCollectionCourses(id, callback) {
	$.ajax({
		url: "/api/me/collections/" + id + "/courses",
		method: "GET",
		data: {
			sort: ["course_code"],
		},
		traditional: true,
		success: (response) => {
			callback(response)
		},
		error: (response) => {
			displayError(response)
		}
	})
}

function getTerm(id, callback) {
	$.ajax({
		url: "/api/terms/" + id,
		method: "GET",
		success: (response) => {
			callback(response)
		},
		error: (response) => {
			displayError(response)
		}
	})
}

function getCourse(id, callback) {
	$.ajax({
		url: "/api/courses/" + id,
		method: "GET",
		success: (response) => {
			callback(response)
		},
		error: (response) => {
			displayError(response)
		}
	})
}

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

// POST

function addCollection(season, year, callback) {
	$.ajax({
		url: "/api/me/collections",
		method: "POST",
		data: {
			season: season,
			year: year
		},
		success: (response) => {
			callback(response)
		},
		error: (response) => {
			displayError(response)
		}
	})
}

function addUserCourse(collection_id, course_id, callback) {
	$.ajax({
		url: "/api/me/course",
		method: "POST",
		data: {
			collection_id: collection_id,
			course_id: course_id
		},
		success: (response) => {
			callback(response)
		},
		error: (response) => {
			displayError(response)
		}
	})
}

// PUT

function putUserCourse(data, callback, onerror = displayError) {
	$.ajax({
		url: "/api/me/course",
		method: "PUT",
		data: data,
		success: (response) => {
			callback(response)
		},
		error: (response) => {
			onerror(response)
		}
	})
}

function putTransferred(set, callback) {
	$.ajax({
		url: "/api/me/sessions/transferred",
		method: "PUT",
		data: {
			set: set
		},
		success: (response) => {
			callback(response)
		},
		error: (response) => {
			displayError(response)
		}
	})
}

// DELETE

function delCollection(id, callback) {
	$.ajax({
		url: "/api/me/collections/" + id,
		method: "DELETE",
		success: (response) => {
			callback(response)
		},
		error: (response) => {
			displayError(response)
		}
	})
}

function removeCollection(id) {
	delCollection(id, () => {
		alert("success", "Term removed!")
		updateCollections()
	})
}

function delUserCourse(id, callback) {
	$.ajax({
		url: "/api/me/course/" + id,
		method: "DELETE",
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

function updateCollections() {
	$("#collectionsContainer .collection-item").remove()
	$("#formEditUserCourse #selectCollection").empty()
	$(".loading").show()
	$(".loaded").hide()
	getCollections((data) => {
		$(".loading").hide()
		$(".loaded").show()
		collections = data.collections
		for (let collection of collections) {
			collection.element = $("#templates .collection-item").clone()
			collection.element.appendTo("#collectionsContainer")
		}
		for (let collection of collections)
			updateCollection(collection.id)
	})
}

function updateCollection(id) {
	let collection = collections.find(c => c.id == id)
	let item = collection.element

	item.find(".collection-course-item").remove()

	item.attr("db-id", id)
	item.find("[db-id]").attr("db-id", id)

	item.find(".loading").show()
	item.find(".loaded").hide()

	item.find("[data-bs-toggle='tooltip']").each((i, e) => {
		new bootstrap.Tooltip(e)
	})

	item.find(".collection-course-container").on("dragover", e => {
		e.preventDefault()
		item.find(".collection-course-container").append($(".dragging"))
		sortCourses(item.find(".collection-course-container"))
	})

	item.find(".countInGPA").change(updateOverallGPA)

	if (collection.term_id) {
		getTerm(collection.term_id, (term) => {
			collection.term_name = term.season.charAt(0).toUpperCase() + term.season.slice(1) + " " + term.year
			collection.term = term
			item.find(".term-name").text(collection.term_name)

			if (term.start || term.end) {
				item.find(".term-date").removeClass("invisible")
				item.find(".term-date .start").text(term.start)
				item.find(".term-date .end").text(term.end)
			}

			if (term.current)
				item.find(".term-current").removeClass("d-none")

			item.find(".collection-remove").attr("title", "Remove term")
			item.find(".collection-remove").attr("onclick", "removeCollection('" + id + "')")

			$("#formEditUserCourse #selectCollection").append(
				$("<option>", {value: collection.id, text: collection.term_name})
			)
		})
	} else if (collection.transfer) {
		collection.term_name = "Transferred"
		item.addClass("transfer")
		item.find(".term-name").text(collection.term_name)
		item.find(".collection-remove").attr("title", "Hide transferred")
		item.find(".collection-remove").attr("onclick", "transferredHide()")
		if (!showTransferred)
			transferredHide()
		$("#formEditUserCourse #selectCollection").append(
			$("<option>", {value: collection.id, text: collection.term_name})
		)
	}

	getCollectionCourses(id, (data) => {
		collection.courses = data.courses

		item.find(".loading").hide()
		item.find(".loaded").show()

		if (Object.keys(collection.courses).length == 0) {
			item.find(".countInGPA").prop("disabled", true)
			item.find(".collection-remove").removeClass("d-none")
		} else if (!collection.transfer) {
			item.find(".collection-remove").addClass("d-none")
		}

		for (let uc of collection.courses)
			updateCollectionCourse(id, uc.id)

		updateOverallGPA()
	})

	if (collection.gpa) {
		item.find(".collection-gpa .gpa").text(collection.gpa.toFixed(2))
		item.find(".collection-gpa .gpa").attr(
			"data-bs-original-title",
			collection.gpa.toFixed(2) + " x " + collection.units + " = " + collection.points + " points"
		)
		item.find(".collection-gpa .nogpa").addClass("d-none")
		item.find(".countInGPA").prop("checked", true)
		collection.element.find(".countInGPA").prop("disabled", false)
	} else {
		item.find(".collection-gpa .gpa").text("")
		item.find(".collection-gpa .nogpa").removeClass("d-none")
		item.find(".countInGPA").prop("checked", false)
		item.find(".countInGPA").prop("disabled", true)
	}
}

function getUpdateCollection(id) {
	getCollection(id, (data) => {
		Object.assign(collections.find(c => c.id == id), data)
		updateCollection(id)
	})
}

function updateCollectionCourse(collection_id, id) {
	let collection = collections.find(c => c.id == collection_id)
	let uc = collection.courses.find(c => c.id == id)

	let item = $("#templates .collection-course-item").clone()

	uc.element = item

	const grade = grades[uc.grade_id]

	item.attr("db-id", id)
	item.attr("db-collection", collection_id)
	item.attr("db-code", uc.course_code)

	item.find(".emoji").html("&#" + (uc.course_emoji ? uc.course_emoji : DEFAULT_EMOJI))
	item.find(".code").text(uc.course_code)
	item.find(".grade").text(uc.grade_id ? grade.symbol : "-")
	item.find(".grade").attr(
		"title",
		uc.grade_id ? ((grade.gpv ? grade.gpv : "-") + " GPV | " + (uc.weightedGPV ? uc.weightedGPV : "-") + " Weighted") : "Grade not set"
	)

	item.get(0).addEventListener("dragstart", () => {
		item.addClass("dragging")
		oldContainer = item.parent().get(0)
	})

	item.get(0).addEventListener("dragend", () => {
		item.removeClass("dragging")
		if (oldContainer != item.parent().get(0)) {
			let newId = item.parent().attr("db-id")
			putUserCourse({
					id: id,
					collection_id: newId
				},
				() => {
					alert("success", "Course moved!")
					getUpdateCollection(collection_id)
					getUpdateCollection(newId)
				},
				(response) => {
					displayError(response)
					updateCollection(collection_id)
					updateCollection(newId)
				}
			)
		}
	})

	item.appendTo(collection.element.find(".collection-course-container"))
}

function updateOverallGPA() {
	overallGPA.sumUnits = 0
	overallGPA.sumPoints = 0
	const overall = $("#overallGPA")
	overall.find("#overallCollectionContainer").empty()

	for (let collection of collections){
		if (collection.element.find(".countInGPA").prop("checked")) {
			overallGPA.sumUnits += collection.units
			overallGPA.sumPoints += collection.points
	
			let item = $("#templates .overall-collection-item").clone()
	
			item.find(".term").text(collection.term_name)
			item.find(".gpa").text(collection.gpa.toFixed(3))
			item.find(".units").text(collection.units.toFixed(2))
			item.find(".points").text(collection.points.toFixed(2))
			item.find(".disable").attr("onclick", "disableOverallGPA('" + collection.id + "')")
	
			$("#overallCollectionContainer").append(item)
		}
	}
	
	overallGPA.finalGPA = overallGPA.sumUnits > 0 ? overallGPA.sumPoints / overallGPA.sumUnits : 0

	overall.find(".sum-points").text(overallGPA.sumPoints.toFixed(2))
	overall.find(".sum-units").text(overallGPA.sumUnits)
	overall.find(".final-gpa").text(overallGPA.finalGPA > 0 ? overallGPA.finalGPA.toFixed(2) : "-")
	overall.find(".final-gpa").attr(
		"title",
		overallGPA.finalGPA > 0 ? overallGPA.finalGPA.toFixed(5) : "-"
	)
}

function disableOverallGPA(id) {
	let collection = collections.find(c => c.id == id)
	collection.element.find(".countInGPA").prop("checked", false)
	updateOverallGPA()
}

//
// EVENTS
//

// Set collection.id input in formAdd whenever its opened
$(document).on("click", ".add-course", function () {
	formAdd.find("#selectCollection").val($(this).attr("db-id"))
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

// On grade changed in form
$("#formEditUserCourse #selectGrade").change(function () {
	$("#formEditUserCourse #selectPassed").prop("checked",
		grades[$(this).val()] ? grades[$(this).val()].passed : false
	)
})

// On key up inside subject selection
$("#selectCourseSubject").on("keyup", function (e) {
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
$("#selectCourseNumber").on("keydown", function (e) {
	// If pressing backspace and the value is empty, move focus to subject selection
	if ($(this).val().length == 0 && e.keyCode == 8)
		formAdd.find(".selectSubject").focus()
})

// On key down inside number selection
$("#selectCourseNumber").on("keyup", function (e) {
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
$(document).on("click", ".collection-course-item", function () {
	if (!$(this).hasClass("dragging")) {
		let collection = collections.find(c => c.id == $(this).attr("db-collection"))
		let uc = collection.courses.find(c => c.id == $(this).attr("db-id"))

		getCourse(uc.course_id, (course) => {
			modalInfo.find(".name").text(course.name)
			modalInfo.find(".link").prop("href", course.url)
			modalInfo.find(".repeat").text(course.repeat ? "Yes" : "No")
			modalInfo.find(".countgpa").text(course.countgpa ? "Yes" : "No")
		})

		if (uc.grade_id) {
			const grade = grades[uc.grade_id]
			modalInfo.find(".grade-symbol").text(grade.symbol)
			modalInfo.find(".grade-desc").text(grade.desc)
			modalInfo.find(".grade-passed").text(grade.passed ? "Yes" : "No")
			if (grade.gpv) {
				modalInfo.find(".grade-gpv").text(grade.gpv.toFixed(2))
				modalInfo.find(".grade-weighted").text((grade.gpv * uc.course_units).toFixed(2))
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
		}

		modalInfo.find(".term").text(collection.term_name)
		modalInfo.find(".emoji").html("&#" + (uc.course_emoji ? uc.course_emoji : DEFAULT_EMOJI))
		modalInfo.find(".code").text(uc.course_code)
		modalInfo.find(".units").text(uc.course_units.toFixed(2))

		formEdit.find("#selectUserCourse").val(uc.id)
		formEdit.find("#selectCoursePlaceholder").val(uc.course_code)
		formEdit.find("#selectCollection").val(collection.id)
		formEdit.find("#selectCollectionOld").val(collection.id)
		formEdit.find("#selectGrade").val(uc.grade_id ? uc.grade_id : 0)
		formEdit.find("#selectPassed").prop("checked", uc.passed ? uc.passed : false)
	}
})

// Form submit

$("#formAddCollection").on("submit", (event) => {
	event.preventDefault()
	event.stopImmediatePropagation()

	let form = $(event.target)

	addCollection(
		form.find("#selectSeason").val(),
		form.find("#selectYear").val(),
		() => {
			alert("success", "Term added!")
			updateCollections()
		}
	)
})

$("#formAddUserCourse").on("submit", (event) => {
	event.preventDefault()
	event.stopImmediatePropagation()

	let form = $(event.target)

	addUserCourse(
		form.find("#selectCollection").val(),
		form.find("#selectCourseId").val(),
		() => {
			alert("success", "Course added!")
			getUpdateCollection(form.find("#selectCollection").val())
		}
	)
})

$("#formEditUserCourse").on("submit", (event) => {
	event.preventDefault()
	event.stopImmediatePropagation()

	let form = $(event.target)
	let method = $(event.originalEvent.submitter).attr("method")

	if (method == "PUT") {
		putUserCourse({
				id: form.find("#selectUserCourse").val(),
				collection_id: form.find("#selectCollection").val(),
				grade_id: form.find("#selectGrade").val(),
				passed: form.find("#selectPassed").prop("checked")
			},
			() => {
				alert("success", "Course updated!")
				getUpdateCollection(form.find("#selectCollection").val())
				if (form.find("#selectCollectionOld").val() != form.find("#selectCollection").val())
					getUpdateCollection(form.find("#selectCollectionOld").val())
			}
		)
	} else if (method == "DELETE") {
		delUserCourse(form.find("#selectUserCourse").val(), () => {
			alert("success", "Course removed!")
			getUpdateCollection(form.find("#selectCollectionOld").val())
		})
	}
})

//
// DOCUMENT READY
//

$(document).ready(updateCollections)
