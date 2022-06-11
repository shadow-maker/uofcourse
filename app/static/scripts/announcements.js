//
// GLOBAL VARS
//

// Init Page object (defined in pagination.html)
var page = new Page(0, () => {
	getAnnouncements((data) => {
		updateResults(data)

		// Announcement passed in URL query parameter
		if (selAnnouncement) {
			let announcement = data.results.find(a => a.id == selAnnouncement)
			if (announcement) { // Announcement in current page data
				$("#modalInfoAnnouncement").modal("show")
				loadModal(announcement)
			} else { // Announcement not in current page data
				getAnnouncement(selAnnouncement, (data) => {
					$("#modalInfoAnnouncement").modal("show")
					loadModal(data)
				})
			}
			// Reset selAnnouncement
			selAnnouncement = null
			// Remove URL query parameter
			window.history.pushState({}, document.title, window.location.pathname)
		}
	})
})

//
// REQUEST FUNCS
// 

function getAnnouncements(callback) {
	$.ajax({
		url: "/api/announcements",
		method: "GET",
		data: {
			sort: ["datetime"],
			asc: false,
			limit: 10,
			page: page.current
		},
		traditional: true,
		success: callback,
		error: displayError
	})
}

function getAnnouncement(id, callback) {
	$.ajax({
		url: "/api/announcements/" + id,
		method: "GET",
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

function loadModal(announcement) {
	const modalInfo = $("#modalInfoAnnouncement")
	modalInfo.find(".title").text(announcement.title)
	modalInfo.find(".datetime").text(announcement.datetime_local.replace("T", " "))
	modalInfo.find(".body").text(announcement.body)
	modalInfo.find(".id").text(announcement.id)
	
	if (isAuth && !announcement.read) {
		putRead(announcement.id, true, (response) => {
			announcement.read = response.read
			if (announcement.element && announcement.read)
				announcement.element.find(".card-header").removeClass("alert-info").addClass("bg-light")
		})
	}
}

function updateResults(data) {
	$(".loading").hide()
	$(".loaded").show()

	$("#announcementsContainer").empty()
	for (let announcement of data.results) {
		announcement.element = $("#templates .announcement-item").clone()

		announcement.element.find(".announcement-title").text(announcement.title)
		announcement.element.find(".announcement-time").text(announcement.datetime_local.replace("T", " "))
		announcement.element.find(".announcement-text").text(announcement.body)

		if (isAuth && !announcement.read)
		announcement.element.find(".card-header").removeClass("bg-light").addClass("alert-info")

		announcement.element.find(".card-header").on("click", () => {
			loadModal(announcement)
		})

		announcement.element.appendTo("#announcementsContainer")
	}

	page.current = data.page
	page.total = data.pages

	page.updateNav()
}
//
// DOCUMENT READY
//

$(document).ready(page.callback)
