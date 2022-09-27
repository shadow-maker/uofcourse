var delay = 30000 // 30 seconds

//
// REQUEST FUNCS
// 

function getCount(callback) {
	$.ajax({
		url: "/api/counters/users",
		method: "GET",
		traditional: true,
		success: callback,
		error: displayError
	})
}

//
// UPDATE FUNCS
//

function updateCount(data) {
	$("#total").text(data.total)
	$("#delay").text(delay / 1000)
}

//
// DOCUMENT READY
//

$(document).ready(() => {
	var i = delay / 1000

	getCount(updateCount)
	$("#remaining").text(i)

	var countInterval = window.setInterval(() => {
		getCount((data) => {
			console.log("Updating count...")
			updateCount(data)

			i = delay / 1000
		})	
	}, delay);	  

	var remainingInterval = window.setInterval(() => {
		i--
		$("#remaining").text(i)
	}, 1000);
})
