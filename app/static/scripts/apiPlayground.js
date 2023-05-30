//
// REQUEST FUNCS
// 

function getRequest(url, callback) {
	$.ajax({
		url: url,
		method: "GET",
		traditional: true,
		complete: callback,
	})
}

//
// DOCUMENT READY
//

$(document).ready(() => {
	$(".loading").hide()
	$("#status").hide()

	$("#makeRequest").on("submit", (e) => {
		e.preventDefault()
		var url = baseURL + "/" + $("#endpoint").val()
		$(".loading").show()
		$("#status").hide()
		getRequest(url, (response) => {
			console.log(response)
			$(".loading").hide()
			$("#status").show()
			$("#requestOutput").text(JSON.stringify(response.responseJSON, null, 2))
			$("#status").text(response.status)
			$("#status").attr("title", response.statusText)
			new bootstrap.Tooltip($("#status"))

			if (response.status == 200)
				$("#status").removeClass("border-danger").removeClass("text-danger").addClass("border-success").addClass("text-success")
			else
				$("#status").removeClass("border-success").removeClass("text-success").addClass("border-danger").addClass("text-danger")
		})
	})
})
