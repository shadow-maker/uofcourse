function reloadResults() {
	page = 1
	$("form").submit()
}

function remSubj(id) {
	$("#subj" + id).remove()
	subjects[id].sel = false
	reloadResults()
}
