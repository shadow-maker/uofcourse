var page = new Page(0, () => {
	requestLogs((data) => {
		updateLogs(data)
	})
})

function requestLogs(callback) {
	$("#logs .loading").show()
	$("#logs .loaded").hide()

	$.ajax({
		url: "/api/users/logs",
		method: "GET",
		data: {
			limit: 10,
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

function requestLocation(id, callback) {
	$.ajax({
		url: "/api/users/logs/" + id + "/location",
		method: "GET",
		success: (response) => {
			callback(response)
		},
		error: (response) => {
			displayError(response)
		}
	})
}

function updateLogs(data) {
	$("#logs .loading").hide()
	$("#logs .loaded").show()

	const logsContainer = $("#logsTable tbody")
	logsContainer.empty()

	for (let log of data.results) {
		let logItem = $("#templates .log-item").clone()

		logItem.find(".id").text(log.id)
		logItem.find(".datetime").text(log.datetime.replace("T", " "))
		logItem.find(".event_type").text(log.event_type)
		logItem.find(".event_name").text(log.event_name)
		logItem.find(".ip-link").attr("db-id", log.id)
		logItem.find(".ip-link .ip").html(log.ip)

		logItem.appendTo("#logsTable tbody")
	}

	page.current = data.page
	page.total = data.pages

	page.updateNav()
}

$(document).on("click", ".ip-link", function (event) {
	event.preventDefault()

	const modal = $("#modalShowLocation")

	modal.find(".loading").show()
	modal.find(".success").hide()
	modal.find(".error").hide()

	modal.find(".ip").val($(this).find(".ip").text())

	requestLocation($(this).attr("db-id"), (data) => {
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

$(document).ready(() => {
	page.current = 1

	requestLogs((response) => {
		updateLogs(response)
	})
})
