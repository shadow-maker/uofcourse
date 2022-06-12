function sortSubjects() {
	if ($("#sortBy").val() != "name" && $("#sortBy").val() != "code")
		return alert("warning", "Invalid sort option '" + $("#sortBy").val() + "'")

	subjects.sort((a, b) => {
		const nameA = a[$("#sortBy").val()].toUpperCase()
		const nameB = b[$("#sortBy").val()].toUpperCase()
		if (nameA < nameB)
			return -1
		if (nameA > nameB)
			return 1
		return 0
	})

	if ($("#orderBy").val() == "0")
		subjects.reverse()
}

function updateSubjects() {
	$("#subjectsContainer").empty()
	for (let subject of subjects) {
		var item = $("#templates .subject-item").clone()

		item.attr("id", "subject-" + subject.id)
	
		item.find(".subject-link").attr("href", subject.url)
		item.find(".subject-emoji").html("&#" + subject.emoji)
		item.find(".subject-code").text(subject.code)
		item.find(".subject-name").text(subject.name)

		item.appendTo("#subjectsContainer")
	}
}

$(document).ready(( ) => {
	sortSubjects()
	updateSubjects()

	$("#subjectsSort select").change(() => {
		sortSubjects()
		updateSubjects()
	})
})
