function updateSubjects() {
	var subjSearch = $("#subjectSearch").val().toUpperCase()
	if (subjSearch in subjects) {
		subjects[subjSearch].sel = true
	}

	$("#subjectSelector").empty()

	for (let s in subjects) {
		if (subjects[s].sel) {
			$("#subjectSelector").append(`
				<span class="bg-secondary px-2 py-1 m-1 rounded mono-font text-light subjItem" code="` + s + `">` + s + `</span>
			`)
		}
	}
}



$(document).ready(function () {
	var suggestions = {}
	$("#subjectSearch").keyup(function () {
		$("#subjectSearchSuggestions").empty()
		var subjSearch = $("#subjectSearch").val().toUpperCase()
		if (subjSearch.length > 0) {
			for (s in subjects) {
				if (s.startsWith(subjSearch)) {
					suggestions[s] = subjects[s]
					$("#subjectSearchSuggestions").append(`
						<li><a class="subjSuggestion dropdown-item form-control-sm px-2 py-1" href="#" code="` + s +`"><span class="mono-font">` +
						s + `</span> - ` + subjects[s].name +
						`</a></li>
					`)
				}
			}
		}
	})
})



$(document).on("click", ".subjItem", function () {
	subjects[this.getAttribute("code")].sel = false
	this.remove()
	$("form").submit()
});

$(document).on("click", ".subjSuggestion", function () {
	$("#subjectSearch").val(this.getAttribute("code"))
	$("form").submit()
	$("#subjectSearchSuggestions").empty()
});