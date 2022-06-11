//
// GLOBAL VARS
//

// Init Page object (defined in pagination.html)
var page = new Page(0, () => {
	$(".loading").show()
	$(".loaded").hide()

	getAnnouncements((data) => {
		$(".loading").hide()
		$(".loaded").show()
	
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
// EXTRA FUNCS
//

function formatDate(date) {
	return date.toLocaleDateString("en-CA", {year: "numeric", month: "long", day: "numeric"})
}

function formatTime(date) {
	return date.toLocaleTimeString("en-CA", {hour: "numeric", minute: "numeric", hour12: false}) 
}

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
	modalInfo.find(".datetime").text(
		formatDate(announcement.datetime_local) + " " + formatTime(announcement.datetime_local) + " MDT"
	)
	modalInfo.find(".datetime").attr("title",
		formatDate(announcement.datetime_utc) + " " + formatTime(announcement.datetime_utc) + " UTC"
	)
	modalInfo.find(".body").text(announcement.body)
	modalInfo.find(".id").text(announcement.id)
	
	if (isAuth && !announcement.read) {
		putRead(announcement.id, true, (response) => {
			announcement.read = response.read
			if (announcement.element && announcement.read) {
				announcement.element.removeClass("alert-info")
				announcement.element.find(".announcement-unread").addClass("invisible")
			}
		})
	}
}

function updateResults(data) {
	$("#announcementsContainer").empty()
	for (let announcement of data.results) {
		announcement.element = $("#templates .announcement-item").clone()

		announcement.element.find(".announcement-title").text(announcement.title)
		announcement.datetime_local = new Date(announcement.datetime_local)
		announcement.datetime_utc = new Date(announcement.datetime_local)
		announcement.element.find(".announcement-time").text(formatDate(announcement.datetime_local))
		announcement.element.find(".announcement-text").text(announcement.body)

		if (isAuth && !announcement.read) {
			announcement.element.addClass("alert-info")
			announcement.element.find(".announcement-unread").removeClass("invisible")
		}

		announcement.element.on("click", () => {
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
