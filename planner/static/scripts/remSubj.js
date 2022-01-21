function updateSubj() {
	text = ""
	for (s of subjSelected) {
		text += s + "-"
	}
	document.getElementById("selectedSubjectsText").setAttribute("value", text.substring(0, text.length - 1))
	document.getElementById("page").setAttribute("value", "1")
	document.getElementById("form").submit()
}

function remSubj(code) {
	$("#subj" + code).remove()
	subjSelected.splice(subjSelected.indexOf(code), 1)
	updateSubj()
}