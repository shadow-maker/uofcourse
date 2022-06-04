//
// GLOBAL VARS
//

var prevData = {}

// Init Page object (defined in pagination.html)
var page = new Page(0, () => {
	requestResults((data) => {
		updateResults(data)
	})
})

//
// REQUEST FUNCS
// 

function requestResults(callback) {
	$("#announcements .loading").show()
	$("#announcements .loaded").hide()

	$.ajax({
		url: "/api/announcements",
		method: "GET",
		data: "json",
		traditional: true,
		success: (response) => {
			callback(response)
			console.log(response)
		},
		error: (response) => {
			$(".loading").hide()
			displayError(response)
			console.log("Error")
		}
	})
}
//
// UPDATE FUNCS
// 

function updateResults(data) {
	$("#announcements .loading").hide()
	$("#announcements .loaded").show()

	const announcementsContainer = $("#announcementsTable tbody")
	announcementsContainer.empty()

	for (let log of data.results) {
		let announcementItem = $("#templates .log-item").clone()

		announcementItem.find(".id").text(log.id)
		announcementItem.find(".datetime").text(log.datetime.replace("T", " "))

		announcementItem.appendTo("#announcementsTable tbody")
	}

	page.current = data.page
	page.total = data.pages

	page.updateNav()
}

//
// DOCUMENT READY
//

$(document).ready(() => {
	page.callback()
})
