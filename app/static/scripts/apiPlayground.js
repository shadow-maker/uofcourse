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

function refreshCodeTheme() {
	const theme = getPreferredTheme()
	if (theme === "light") {
		$("#codeLight").prop("disabled", false)
		$("#codeDark").prop("disabled", true)
	} else if (theme === "dark") {
		$("#codeLight").prop("disabled", true)
		$("#codeDark").prop("disabled", false)
	}
}

//
// DOCUMENT READY
//

window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", refreshCodeTheme)

$(document).ready(() => {
	$(".loading").hide()
	$("#status").hide()

	refreshCodeTheme()
	hljs.highlightElement($("#requestOutput")[0])

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
			hljs.highlightElement($("#requestOutput")[0])
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
