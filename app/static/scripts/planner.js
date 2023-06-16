//
// GLOBAL VARS
//

let firstDrag = false

let collections = []
let courseCanMoveTo = []
let courseOldCollection = null
let overallGPA = {
	sumUnits: 0,
	sumGPA: 0,
	finalGPA: 0
}

const dateFormatLocale = "en-US"
const dateFormatOptions = { month: "short", day: "2-digit" }

const modalInfo = $("#modalInfoCollectionCourse")
const formAdd = $("#formAddCollectionCourse")
const formEdit = $("#formEditCollectionCourse")

//
// UTIL FUNCS
//

function transferredShow() {
	let callback = () => {
		$(".transfer").removeClass("d-none")
		$("#transfer-collapsed").addClass("d-none")
	}

	if (!showTransferred) {
		showTransferred = true
		putTransferred(showTransferred, callback)
	} else {
		callback()
	}
}

function transferredHide() {
	let callback = () => {
		$(".transfer").addClass("d-none")
		$("#transfer-collapsed").removeClass("d-none")
		$(".transfer").find(".countInGPA").prop("checked", false)
		updateOverallGPA()
	}

	if (showTransferred) {
		showTransferred = false
		putTransferred(showTransferred, callback)
	} else {
		callback()
	}
}

function formAddCustomOff() {
	$("#selectCourseCustom").prop("checked", false);
	$("#customCoursePrompt").addClass("invisible")
	$("#customCourseFields").addClass("d-none")
	$("#customCourseSubmit").addClass("d-none")
	$("#selectCourseSubmit").removeClass("d-none")
	$("#selectCourseSubmit").prop("disabled", true)
}

function formAddCustomOn() {
	$("#selectCourseCustom").prop("checked", true);
	$("#customCoursePrompt").addClass("invisible")
	$("#customCourseFields").removeClass("d-none")
	$("#selectCourseSubmit").addClass("d-none")
	$("#customCourseSubmit").removeClass("d-none")
	$("#customCourseSubmit").prop("disabled", false)

	$("#customCourseName").val("")
	$("#customCourseUnits").val(3.00)
	$("#customCourseRepeat").prop("checked", false)
	$("#customCourseCountGPA").prop("checked", true)
}

function collapse(element) {
	$(element).find(".toggleOn").toggle()
	$(element).find(".toggleOff").toggle()
}

// Check course funcs for add modal

function selectCourseStatus(status, message = "") {
	$("#selectCourseStatus").addClass("invisible")
	$("#selectCourseStatus .message").html("...")
	if (status) {
		$("#selectCourseStatus").children("span").hide()
		$("#selectCourseStatus ." + status).show()
		$("#selectCourseStatus .message").html(message)
		$("#selectCourseStatus").removeClass("invisible")
	}
}

function checkCourse() {
	addCollectionCourseCheck(
		formAdd.find("#selectCollection").val(),
		$("#selectCourseSubject").val(),
		$("#selectCourseNumber").val(),
		(response) => {
			if (response.error) {
				$("#selectCourseId").val("")
				$("#selectCourseSubmit").prop("disabled", true)
				selectCourseStatus("error", response.error)
			} else {
				if (response.success) {
					selectCourseStatus("success", response.success)
					$("#customCoursePrompt").addClass("invisible")
				} else {
					let warnings = ""
					for (let w of response.warnings)
						warnings += w + "<br>"
					selectCourseStatus("warning", warnings)
				}
				if (response.course_id == null) {
					$("#customCoursePrompt").removeClass("invisible")
				} else {
					$("#selectCourseId").val(response.course_id)
					$("#selectCourseSubmit").prop("disabled", false)
				}
			}
		}
	)
}

//
// REQUEST FUNCS
//

// GET

function getCollections(callback) {
	ajax("GET", "me/collections", { sort: ["term_id"] }, callback)
}

function getCollection(id, callback) {
	ajax("GET", "me/collections/" + id, {}, callback)
}

function getCollectionCourses(id, callback) {
	ajax("GET", "me/collections/" + id + "/courses", { sort: ["course_code"] }, callback)
}

function getTerm(id, callback) {
	ajax("GET", "terms/" + id, {}, callback)
}

function getCourse(collection_course_id, callback) {
	ajax("GET", "me/courses/" + collection_course_id + "/course", {}, callback)
}

function getProgress(callback) {
	ajax("GET", "me/planner/progress", {}, callback)
}

function getSummary(x, y, show, taken, planned, callback) {
	ajax("GET", "me/planner/summary",
		{ x: x, y: y, show: show, taken: taken, planned: planned },
		callback
	)
}

function getWarnings(callback) {
	ajax("GET", "me/planner/warnings", {}, callback)
}

// POST

function addCollection(season, year, callback) {
	ajax("POST", "me/collections",
		{
			season: season,
			year: year
		},
		callback
	)
}

function addCollectionCourseCheck(collection_id, code, number, callback) {
	ajax("POST", "me/courses/check",
		{
			collection_id: collection_id,
			subject_code: code,
			course_number: number
		},
		callback
	)
}

function addCollectionCourse(data, callback) {
	ajax("POST", "me/courses",
		data,
		callback
	)
}

// PUT

function putCollectionCourse(data, callback, onerror = displayError) {
	ajax("PUT", "me/courses", data, callback, onerror)
}

function putTransferred(set, callback) {
	ajax("PUT", "me/sessions/transferred", { set: set }, callback)
}

function putUnitsNeeded(units, callback) {
	ajax("PUT", "me/planner/progress", { units_needed: units }, callback)
}

// DELETE

function delCollection(id, callback) {
	ajax("DELETE", "me/collections/" + id, {}, callback)
}

function removeCollection(id) {
	delCollection(id, () => {
		alert("success", "Term removed!")
		updateCollections()
	})
}

function delCollectionCourse(id, callback) {
	ajax("DELETE", "me/courses/" + id, {}, callback)
}

//
// UPDATE FUNCS
//

function updateCollections() {
	$("#collectionsContainer .collection-item").remove()
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
			updateCollection(collection.id, false)
		updateWarnings()
		updateOverallGPA()
	})
}

function updateCollection(id, updateWidgets = true) {
	let collection = collections.find(c => c.id == id)
	let item = collection.element

	item.find(".collection-course-item").remove()

	item.find(".loading").show()
	item.find(".loaded").hide()

	item.find(".collection-course-container").attr("db-id", id)

	item.find(".countInGPA").change(updateOverallGPA)
	item.find(".add-course").attr("onclick", "$('#formAddCollectionCourse #selectCollection').val(" + id + ")")


	// Init tooltips
	item.find("[data-bs-toggle='tooltip']").each((i, e) => {
		new bootstrap.Tooltip(e)
	})

	// Events

	item.find(".collection-course-container").on("dragover", e => {
		e.preventDefault()
		if (!collection.dragover) {
			collection.dragover = true
			if (courseCanMoveTo.includes(collection.id)) {
				item.addClass("dragover-success")
				const container = item.find(".collection-course-container")
				const dragging = $(".dragging")
				// Place dragging item in correct position (assumes collection.courses is sorted)
				let inserted = false
				for (let course of collection.courses) {
					if (course.course_code.toLowerCase() > dragging.attr("db-code").toLowerCase()) {
						dragging.insertBefore(course.element)
						inserted = true
						break
					}
				}
				if (!inserted)
					dragging.appendTo(container)
			} else {
				item.addClass("dragover-danger")
				let match = collection.courses.find(c => c.course_code == $(".dragging").attr("db-code"))
				match.element.addClass("drag-course-match")
			}
		}
	})

	item.find(".collection-course-container").on("dragleave", e => {
		e.preventDefault()
		if (collection.dragover) {
			collection.dragover = false
			item.removeClass("dragover-success").removeClass("dragover-danger")
			for (let course of collection.courses)
				course.element.removeClass("drag-course-match")
		}
	})

	// Set term specific data
	if (collection.term_id) {
		getTerm(collection.term_id, (term) => {
			collection.term_name = term.season.charAt(0).toUpperCase() + term.season.slice(1) + " " + term.year
			collection.term = term
			item.find(".term-name").text(collection.term_name)

			if (term.start || term.end) {
				item.find(".term-date").removeClass("invisible")

				const start = new Date(term.start)
				item.find(".term-date .start").text(start.toLocaleDateString(dateFormatLocale, dateFormatOptions))

				const end = new Date(term.end)
				item.find(".term-date .end").text(end.toLocaleDateString(dateFormatLocale, dateFormatOptions))
			}

			if (term.current)
				item.find(".term-current").removeClass("d-none")

			item.find(".collection-remove").attr("title", "Remove term")
			item.find(".collection-remove").attr("onclick", "removeCollection('" + id + "')")
		})
	} else if (collection.transfer) {
		collection.term_name = "Transferred"
		item.addClass("transfer")
		item.find(".term-name").text(collection.term_name)
		item.find(".collection-remove").attr("title", "Hide transferred")
		item.find(".collection-remove").attr("onclick", "transferredHide()")
		if (!showTransferred)
			transferredHide()
	}

	// Update GPA data
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

	// Get and update collection courses
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

		for (let cc of collection.courses)
			updateCollectionCourse(id, cc.id)

		if (updateWidgets) {
			updateWarnings()
			updateOverallGPA()
		}
	})
}

function getUpdateCollection(id, updateWidgets = true) {
	getCollection(id, (data) => {
		Object.assign(collections.find(c => c.id == id), data)
		updateCollection(id, updateWidgets)
	})
}

function updateCollectionCourse(collection_id, id) {
	const collection = collections.find(c => c.id == collection_id)
	const cc = collection.courses.find(c => c.id == id)

	if (cc.element)
		cc.element.remove()

	cc.element = $("#templates .collection-course-item").clone()

	const grade = grades[cc.grade_id]

	cc.element.attr("db-code", cc.course_code)

	cc.element.find(".emoji").html("&#" + (cc.course_emoji ? cc.course_emoji : DEFAULT_EMOJI))
	cc.element.find(".code").text(cc.course_code)
	cc.element.find(".grade").text(cc.grade_id ? grade.symbol : "-")
	cc.element.find(".grade").attr(
		"title",
		cc.grade_id ? ((grade.gpv != null ? grade.gpv : "-") + " GPV | " + (cc.weightedGPV != null ? cc.weightedGPV : "-") + " Weighted") : "Grade not set"
	)

	// Item events

	cc.element.on("click", () => {
		if (cc.element.hasClass("dragging"))
			return

		modalInfo.find(".name").text("Loading...")
		modalInfo.find(".link").prop("href", "")
		modalInfo.find(".repeat").text("Loading...")
		modalInfo.find(".countgpa").text("Loading...")
		modalInfo.find(".not-available").addClass("d-none")

		modalInfo.find(".term").text(collection.term_name)
		modalInfo.find(".emoji").html("&#" + (cc.course_emoji ? cc.course_emoji : DEFAULT_EMOJI))
		modalInfo.find(".code").text(cc.course_code)
		modalInfo.find(".units").text(cc.course_units.toFixed(2))
		if (cc.calendar_url) {
			modalInfo.find(".calendarurl a").prop("href", cc.calendar_url)
			modalInfo.find(".calendarurl").removeClass("d-none")
		} else {
			modalInfo.find(".calendarurl a").prop("href", "")
			modalInfo.find(".calendarurl").addClass("d-none")
		}

		if (cc.custom) {
			modalInfo.find(".code-custom").removeClass("d-none")
			modalInfo.find(".code-link").addClass("d-none")
		} else {
			modalInfo.find(".code-custom").addClass("d-none")
			modalInfo.find(".code-link").removeClass("d-none")
		}

		getCourse(cc.id, (course) => {
			modalInfo.find(".name").text(course.name)
			modalInfo.find(".link").prop("href", course.url)
			modalInfo.find(".repeat").text(course.repeat ? "Yes" : "No")
			modalInfo.find(".countgpa").text(course.countgpa ? "Yes" : "No")
			if (!cc.custom && !cc.calendar_available)
				modalInfo.find(".not-available").removeClass("d-none")
		})

		if (cc.grade_id) {
			const grade = grades[cc.grade_id]
			modalInfo.find(".grade-symbol").text(grade.symbol)
			modalInfo.find(".grade-desc").text(grade.desc)
			modalInfo.find(".grade-passed").text(grade.passed ? "Yes" : "No")
			if (grade.gpv != null) {
				modalInfo.find(".grade-gpv").text(grade.gpv.toFixed(2))
				modalInfo.find(".grade-weighted").text((grade.gpv * cc.course_units).toFixed(2))
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

		formEdit.find("#selectCollectionCourse").val(cc.id)
		formEdit.find("#selectCoursePlaceholder").val(cc.course_code)
		formEdit.find("#selectGrade").val(cc.grade_id ? cc.grade_id : 0)
		formEdit.find("#selectPassed").prop("checked", cc.passed ? cc.passed : false)

		$("#formEditCollectionCourse #selectCollection").empty()
		for (let c of collections) {
			$("#formEditCollectionCourse #selectCollection").append(
				$("<option>", {
					value: c.id,
					text: c.term_name
				})
			)
		}
		formEdit.find("#selectCollection").val(collection.id)
		formEdit.find("#selectCollectionOld").val(collection.id)
	})

	cc.element.get(0).addEventListener("dragstart", () => {
		cc.element.addClass("dragging")
		courseOldCollection = collection_id
		courseCanMoveTo = []
		for (let collec of collections)
			if (collec.id == collection_id || !collec.courses.find(c => c.course_id == cc.course_id))
				courseCanMoveTo.push(collec.id)
		if (!firstDrag) {
			alert("info", "Drag course to move to another term")
			firstDrag = true
		}
	})

	cc.element.get(0).addEventListener("dragend", () => {
		cc.element.removeClass("dragging")
		const newId = parseInt(cc.element.parent().attr("db-id"))
		if (courseOldCollection != newId && courseCanMoveTo.includes(newId)) {
			putCollectionCourse({ id: cc.id, collection_id: newId },
				(response) => {
					alert("success", "Course moved!")
					for (let w of response.warnings)
						alert("warning", w)
					getUpdateCollection(collection_id, false)
					getUpdateCollection(newId)
					updateProgress()
				},
				(response) => {
					displayError(response)
					updateCollection(collection_id)
					updateCollection(newId)
				}
			)
		}
		for (let collec of collections) {
			collec.element.removeClass("dragover-success").removeClass("dragover-danger")
			for (let c of collec.courses)
				c.element.removeClass("drag-course-match")
		}
	})

	cc.element.appendTo(collection.element.find(".collection-course-container"))

	// CollectionCourse id was passed as URL parameter
	if (selCollectionCourse && selCollectionCourse == cc.id) {
		cc.element.click()
		selCollectionCourse = null
		window.history.pushState({}, document.title, window.location.pathname)
	}
}

function updateWarnings() {
	getWarnings((response) => {
		if (response.warnings.length == 0) {
			$("#plannerWarnings").addClass("d-none")
		} else {
			$("#plannerWarnings").removeClass("d-none")
			$("#plannerWarningsContainer").empty()
			for (let w of response.warnings)
				$("#plannerWarningsContainer").append($("<li>", { text: w }))
		}
	})
}

function updateOverallGPA() {
	overallGPA.sumUnits = 0
	overallGPA.sumPoints = 0
	const overall = $("#overallGPA")
	overall.find("#overallCollectionContainer").empty()

	for (let collection of collections) {
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

function updateProgress() {
	getProgress((data) => {
		if (data.units_needed) {
			const progressBar = $("#progress .bar")
			const progressInfo = $("#progress .info")
			let unitsTakenPercent = (data.units_taken / data.units_needed) * 100
			let unitsTotalPercent = ((data.units_taken + data.units_planned) / data.units_needed) * 100

			progressBar.find(".units-taken").attr("aria-valuenow", Math.round(unitsTakenPercent))
			progressBar.find(".units-taken").css(
				"width",
				Math.round(unitsTakenPercent) + "%"
			)

			progressBar.find(".units-planned").attr("aria-valuenow", Math.round(unitsTotalPercent))
			progressBar.find(".units-planned").css(
				"width",
				Math.round(
					(unitsTotalPercent < 100 ? unitsTotalPercent : 100) - unitsTakenPercent
				) + "%"
			)

			progressBar.find(".units-missing").attr("aria-valuenow", Math.round(100 - unitsTotalPercent))
			progressBar.find(".units-missing").css(
				"width",
				Math.round(unitsTotalPercent < 100 ? 100 - unitsTotalPercent : 0) + "%"
			)
			$("#progress").find(".units-taken-percent").text(unitsTakenPercent.toFixed(1))
			progressBar.find(".units-planned-percent").text(unitsTotalPercent.toFixed(1))

			progressInfo.find(".units-taken").text(data.units_taken)
			progressInfo.find(".units-planned").text(data.units_planned)
			progressInfo.find(".units-taken-planned").text(data.units_taken + data.units_planned)

			progressInfo.find(".units-missing-taken").text(data.units_needed - data.units_taken)
			progressInfo.find(".units-missing-taken-planned").text(data.units_needed - data.units_taken - data.units_planned)

			progressInfo.find(".units-needed").text(data.units_needed)

			$("#selectUnitsNeeded").val(data.units_needed)
		} else {
			progressBar.find(".units-taken").attr("aria-valuenow", "")
			progressBar.find(".units-taken").css("width", "0%")
			progressBar.find(".units-planned").attr("aria-valuenow", "")
			progressBar.find(".units-planned").css("width", "0%")
			progressBar.find(".units-taken-percent").text("-")
			progressBar.find(".units-planned-percent").text("-")

			progressInfo.find(".units-taken").text("-")
			progressInfo.find(".units-planned").text("-")
			progressInfo.find(".units-taken-planned").text("-")

			progressInfo.find(".units-missing-taken").text("-")
			progressInfo.find(".units-missing-taken-planned").text("-")

			progressInfo.find(".units-needed").text("-")

			$("#selectUnitsNeeded").val("")
		}
	})
}

function updateSummary() {
	let x = $("#summarySelectX").val()
	let y = $("#summarySelectY").val()
	y = y == "none" ? null : y

	let show = $("#summarySelectShow").val()
	let taken = $("#summarySelectTaken").is(":checked")
	let planned = $("#summarySelectPlanned").is(":checked")

	function getKey(option, key) {
		if (option == "terms") {
			if (key == "none") {
				key = "transferred"
			} else {
				let collection = collections.find(c => c.term_id == key)
				key = collection ? collection.term_name : key
			}
		}
		return key[0].toUpperCase() + key.substring(1)
	}

	getSummary(x, y, show, taken, planned, (data) => {
		$("#summary thead tr").empty()
		$("#summary tbody").empty()
		if (y)
			$("#summary thead tr").append($("<td>").attr("scope", "col"))

		for (let xKey of data.x_keys)
			$("#summary thead tr").append(
				$("<td>").attr("scope", "col").text(getKey(x, xKey))
			)

		if (y) {
			for (let yKey of data.y_keys) {
				let row = $("<tr>")
				row.append(
					$("<td>").attr("scope", "row").text(getKey(y, yKey)).addClass("table-active")
				)
				for (let xKey of data.x_keys)
					row.append($("<td>").text(data.results[xKey][yKey]))
				$("#summary tbody").append(row)
			}
		} else {
			let row = $("<tr>")
			for (let xKey in data.results)
				row.append($("<td>").text(data.results[xKey]))
			$("#summary tbody").append(row)
		}

		for (let i of $("#summarySelectX").find("option"))
			$(i).prop("disabled", $(i).val() == y)

		for (let i of $("#summarySelectY").find("option"))
			$(i).prop("disabled", $(i).val() == x)
	})
}

//
// EVENTS
//

// On modal starts to show
$("#modalAddCourse").on("show.bs.modal", () => {
	// Clear form inputs
	formAdd.find(".selectSubject").val("")
	formAdd.find(".selectNumber").val("")

	// Hide status
	selectCourseStatus()

	formAddCustomOff()
})

// On modal is shown - move focus to input
$("#modalAddCourse").on("shown.bs.modal", () => {
	formAdd.find(".selectSubject").focus()
})

$("#modalEditUnits").on("shown.bs.modal", () => {
	let value = $("#formEditUnits #selectUnitsNeeded").val()
	$("#formEditUnits #selectUnitsNeeded").val("").focus().val(value)
})

// On grade changed in form
$("#formEditCollectionCourse #selectGrade").on("change", function () {
	$("#formEditCollectionCourse #selectPassed").prop("checked",
		grades[$(this).val()] ? grades[$(this).val()].passed : false
	)
})

// On summary options changed
$("#summary select").on("change", function () {
	updateSummary()
})
$("#summary input").on("change", function () {
	updateSummary()
})

// On key up inside subject selection
$("#selectCourseSubject").on("keyup", function (e) {
	// Remove special characters
	$(this).val($(this).val().replace(/[^a-zA-Z]/g, "").toUpperCase())

	if ($(this).val().length < $(this).attr("minLength")) {
		formAdd.find(".selectNumber").prop("disabled", true)
		formAddCustomOff()
		selectCourseStatus()
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
	// Remove special characters
	$(this).val($(this).val().replace(/[^a-zA-Z0-9]/g, "").toUpperCase())

	// Check course if length is complete
	if ($(this).val().length == $(this).attr("maxLength")) {
		checkCourse()
	} else {
		formAddCustomOff()
		selectCourseStatus()
	}
})

// Form submit

$("#formAddCollection").on("submit", (event) => {
	event.preventDefault()
	event.stopImmediatePropagation()

	let form = $("#formAddCollection")

	addCollection(
		form.find("#selectSeason").val(),
		form.find("#selectYear").val(),
		() => {
			alert("success", "Term added!")
			updateCollections()
		}
	)
})

$("#customCoursePrompt").on("click", () => {
	formAddCustomOn()
})

$("#formAddCollectionCourse").on("submit", (event) => {
	event.preventDefault()
	event.stopImmediatePropagation()

	data = { collection_id: formAdd.find("#selectCollection").val() }

	if (formAdd.find("#selectCourseCustom").prop("checked")) {
		// Custom course
		data.custom = true
		data.subject_code = formAdd.find("#selectCourseSubject").val()
		data.number = formAdd.find("#selectCourseNumber").val()
		data.name = formAdd.find("#customCourseName").val()
		data.units = parseFloat(formAdd.find("#customCourseUnits").val())
		data.repeat = formAdd.find("#customCourseRepeat").prop("checked")
		data.countgpa = formAdd.find("#customCourseCountGPA").prop("checked")
	} else {
		// Existing course
		data.custom = false
		data.course_id = formAdd.find("#selectCourseId").val()
	}
	addCollectionCourse(data, (response) => {
		alert("success", "Course added!")
		for (let w of response.warnings)
			alert("warning", w)
		getUpdateCollection(formAdd.find("#selectCollection").val())
		updateProgress()
		updateSummary()
	})

})

$("#formEditCollectionCourse").on("submit", (event) => {
	event.preventDefault()
	event.stopImmediatePropagation()

	let form = $(event.target)
	let method = $(event.originalEvent.submitter).attr("method")

	if (method == "PUT") {
		putCollectionCourse({
			id: form.find("#selectCollectionCourse").val(),
			collection_id: form.find("#selectCollection").val(),
			grade_id: form.find("#selectGrade").val(),
			passed: form.find("#selectPassed").prop("checked")
		},
			() => {
				alert("success", "Course updated!")
				getUpdateCollection(form.find("#selectCollection").val())
				if (form.find("#selectCollectionOld").val() != form.find("#selectCollection").val())
					getUpdateCollection(form.find("#selectCollectionOld").val(), false)
				updateProgress()
				updateSummary()
			}
		)
	} else if (method == "DELETE") {
		delCollectionCourse(form.find("#selectCollectionCourse").val(), () => {
			alert("success", "Course removed!")
			getUpdateCollection(form.find("#selectCollectionOld").val())
			updateProgress()
			updateSummary()
		})
	}
})

$("#formEditUnits").on("submit", (event) => {
	event.preventDefault()
	event.stopImmediatePropagation()

	let form = $("#formEditUnits")

	putUnitsNeeded(parseFloat(form.find("#selectUnitsNeeded").val()), () => {
		alert("success", "Units needed updated!")
		updateProgress()
	})
})

//
// DOCUMENT READY
//

$(document).ready(() => {
	updateCollections()
	updateProgress()
	updateSummary()
})
