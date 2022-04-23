var page = new Page(0, () => {
	requestLogs((data) => {
		updateLogs(data)
	})
})

function requestLogs(callback) {
	$(".loading").show()
	$(".loaded").hide()

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

function updateLogs(data) {
	$(".loading").hide()
	$(".loaded").show()

	const logsContainer = $("#logsTable tbody")
	logsContainer.empty()

	for (let log of data.results) {
		let logItem = $("#templates .log-item").clone()

		logItem.find(".id").text(log.id)
		logItem.find(".datetime").text(log.datetime.replace("T", " "))
		logItem.find(".event_type").text(log.event_type)
		logItem.find(".event_name").text(log.event_name)
		logItem.find(".ip").text(log.ip)

		logItem.appendTo("#logsTable tbody")
	}

	page.current = data.page
	page.total = data.pages

	page.updateNav()
}

//
// DOCUMENT READY
//

$(document).ready(() => {
	page.current = 1

	requestLogs((response) => {
		updateLogs(response)
	})
})
