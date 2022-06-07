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

function putRead(id, callback) {
	$.ajax({
		url: "/api/announcements/" + id + "/read",
		method: "PUT",
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

function updateResults(data) {
	$(".loading").hide()
	$(".loaded").show()

	$("#announcementsContainer").empty()
	for (let announcement of data.results) {
		let announcementItem = $("#templates .announcement-item").clone()

		announcementItem.find(".announcement-title").text(announcement.title)
		announcementItem.find(".announcement-time").text(announcement.datetime.replace("T", " "))
		announcementItem.find(".announcement-text").text(announcement.body)

		if (isAuth && !announcement.read)
			announcementItem.find(".card-header").removeClass("bg-light").addClass("alert-info")

		announcementItem.find(".card-header").click(e => {
			const modalInfo = $("#modalInfoAnnouncement")
			modalInfo.find(".title").text(announcement.title)
			modalInfo.find(".datetime").text(announcement.datetime.replace("T", " "))
			modalInfo.find(".body").text(announcement.body)
			modalInfo.find(".id").text(announcement.id)

			announcementItem.find(".card-header").removeClass("alert-info").addClass("bg-light")
			
			putRead(announcement.id, (response) => {
				console.log(response)
				announcementItem.find(".card-header").removeClass("alert-info").addClass("bg-light")
			})
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