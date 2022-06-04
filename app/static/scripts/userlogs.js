//
// GLOBAL VARS
//

// Init Page object (defined in pagination.html)
var page = new Page(0, () => {
	getLogs((data) => {
		updateLogs(data)
	})
})

//
// REQUEST FUNCS
//

function getLogs(callback) {
	$("#logs .loading").show()
	$("#logs .loaded").hide()

	$.ajax({
		url: "/api/me/logs",
		method: "GET",
		data: {
			sort: ["datetime"],
			asc: false,
			limit: 15,
			page: page.current
		},
		traditional: true,
		success: (response) => {callback(response)},
		error: (response) => {
			$(".loading").hide()
			displayError(response)
		}
	})
}

function getLocation(id, callback) {
	$.ajax({
		url: "/api/me/logs/" + id + "/location",
		method: "GET",
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

function showDatetime(timezone) {
	$("#logsTable tbody .datetime span").addClass("d-none")
	$("#logsTable tbody .datetime ." + timezone).removeClass("d-none")
}

function updateLogs(data) {
	$("#logs .loading").hide()
	$("#logs .loaded").show()

	const logsContainer = $("#logsTable tbody")
	logsContainer.empty()

	for (let log of data.results) {
		let logItem = $("#templates .log-item").clone()

		logItem.find(".id").text(log.id)
		logItem.find(".datetime .utc").text(
			log.datetime_utc.substring(0, log.datetime_utc.lastIndexOf(
				log.datetime_utc.includes("+") ? "+" : "-"
			)).replace("T", " ")
		)
		logItem.find(".datetime .local").text(
			log.datetime_local.substring(0, log.datetime_local.lastIndexOf(
				log.datetime_local.includes("+") ? "+" : "-"
			)).replace("T", " ")
		)
		logItem.find(".event_type").text(log.event_type)
		logItem.find(".event_name").text(log.event_name)
		logItem.find(".ip-link").attr("db-id", log.id)
		logItem.find(".ip-link .ip").html(log.ip)

		logItem.appendTo("#logsTable tbody")
	}

	showDatetime("utc")

	page.current = data.page
	page.total = data.pages

	page.updateNav()
}

//
// Events
//

$(document).on("change", "#logsTimezoneSelect", function (event) {
	showDatetime($(this).val())
})

$(document).on("click", ".ip-link", function (event) {
	event.preventDefault()

	const modal = $("#modalShowLocation")

	modal.find(".loading").show()
	modal.find(".success").hide()
	modal.find(".error").hide()

	modal.find(".ip").val($(this).find(".ip").text())

	getLocation($(this).attr("db-id"), (data) => {
		modal.find(".loading").hide()
		if (data.status == "success") {
			modal.find(".success").show()
			for (property in data)
				modal.find(".success ." + property).text(data[property])
			modal.find(".success .gmaps-link").attr("href", data.gmaps)
		} else {
			modal.find(".error").show()
			modal.find(".error .message").text(data.message)
		}
	})

	modal.modal("show")
})

//
// DOCUMENT READY
//

$(document).ready(page.callback)
