function updateSubjects() {
	var subjSearch = $("#subjectSearch").val().toUpperCase()
	$("#subjectSearch").val("")

	if (subjSearch in subjects)
		subjects[subjSearch].sel = true

	$("#subjectSelector").empty()

	for (let s in subjects) {
		if (subjects[s].sel) {
			$("#subjectSelector").append(`
				<span class="badge btn btn-secondary border-secondary px-1 py-1 m-1 ms-0 font-monospace text-light fs-6 fw-normal subjItem" code="` + s + `"  title="Click to remove">
					` + s + `
				</span>
			`)
		}
	}
}

$(document).ready(() => {
	$("#subjectSearch").keyup(function () {
		$("#subjectSearchSuggestions").empty()
		var subjSearch = $("#subjectSearch").val().toUpperCase()
		if (subjSearch.length > 0) {
			for (s in subjects) {
				if (s.startsWith(subjSearch)) {
					$("#subjectSearchSuggestions").append(`
						<li><a class="subjSuggestion dropdown-item form-control-sm px-2 py-1" href="#" code="` + s +`"><span class="font-monospace">` +
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
	$("#formFilterCourses").submit()
});

$(document).on("click", ".subjSuggestion", function () {
	$("#subjectSearch").val(this.getAttribute("code"))
	$("#subjectSearchSuggestions").empty()
	$("#formFilterCourses").submit()
});