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
			limit: 8,
			page: page.current
		},
		traditional: true,
		success: callback,
		error: displayError
	})
}

function putRead(id, set, callback) {
	$.ajax({
		url: "/api/announcements/" + id + "/read",
		method: "PUT",
		data: {set: set},
		success: callback,
		error: displayError
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
		let item = $("#templates .announcement-item").clone()

		item.find(".announcement-title").text(announcement.title)
		item.find(".announcement-time").text(announcement.datetime.replace("T", " "))
		item.find(".announcement-text").text(announcement.body)

		if (isAuth && !announcement.read)
			item.find(".card-header").removeClass("bg-light").addClass("alert-info")

		item.find(".card-header").click(e => {
			const modalInfo = $("#modalInfoAnnouncement")
			modalInfo.find(".title").text(announcement.title)
			modalInfo.find(".datetime").text(announcement.datetime.replace("T", " "))
			modalInfo.find(".body").text(announcement.body)
			modalInfo.find(".id").text(announcement.id)

			item.find(".card-header").removeClass("alert-info").addClass("bg-light")
			
			if (isAuth && !announcement.read) {
				putRead(announcement.id, true, (response) => {
					item.find(".card-header").removeClass("alert-info").addClass("bg-light")
					announcement.read = response.read
				})
			}
		})
	
		item.appendTo("#announcementsContainer")

		if (announcement.id == announcementID) {
			var modalInfo = $("#modalInfoAnnouncement")
			modalInfo.find(".title").text(announcement.title)
			modalInfo.find(".datetime").text(announcement.datetime.replace("T", " "))
			modalInfo.find(".body").text(announcement.body)
			modalInfo.find(".id").text(announcement.id)
			modalInfo.modal("show")
		}
	}

	page.current = data.page
	page.total = data.pages

	page.updateNav()
}
//
// DOCUMENT READY
//

$(document).ready(page.callback)
