function updateSubj() {
	document.getElementById("page").setAttribute("value", "1")
	document.getElementById("form").submit()
}

function remSubj(id) {
	$("#subj" + id).remove()
	$("#subjCheck" + id).prop("checked", false);
	subjects[id].sel = false
	document.getElementById("page").setAttribute("value", "1")
	document.getElementById("form").submit()
}