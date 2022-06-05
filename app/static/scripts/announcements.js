//
// GLOBAL VARS
//

// Init Page object (defined in pagination.html)
var page = new Page(0, () => {
	requestResults(updateResults)
})

//
// REQUEST FUNCS
// 

function requestResults(callback) {
	$.ajax({
		url: "/api/announcements",
		method: "GET",
		data: {
			sort: ["datetime"],
			asc: false,
			limit: 5,
			page: page.current
		},
		traditional: true,
		success: (response) => {
			callback(response)
			console.log(response)
		},
		error: (response) => {
			displayError(response)
			console.log("Error")
		}
	})
}
//
// UPDATE FUNCS
// 

function updateResults(data) {
	$(".loading").hide()
	$(".loaded").show()

	$("#announcementsContainer").empty()
	for (let announcement of data.results) {
		let announcementItem = $("#templates .announcement-item").clone()

		announcementItem.find(".announcement-title").text(announcement.title)
		announcementItem.find(".announcement-time").text(announcement.datetime.replace("T", " "))
		announcementItem.find(".announcement-text").text(announcement.body)

		announcementItem.find(".card-header").click(e => {
			const modalInfo = $("#modalInfoAnnouncement")
			modalInfo.find(".title").text(announcement.title)
			modalInfo.find(".datetime").text(announcement.datetime.replace("T", " "))
			modalInfo.find(".body").text(announcement.body)
			modalInfo.find(".id").text(announcement.id)
		})

		announcementItem.appendTo("#announcementsContainer")
	}

	page.current = data.page
	page.total = data.pages

	page.updateNav()
}
//
// DOCUMENT READY
//

$(document).ready(page.callback)
