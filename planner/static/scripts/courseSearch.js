function reloadResults() {
	$("#page").attr("value", "1")
	$("#form").submit()
}

function remSubj(id) {
	$("#subj" + id).remove()
	$("#subjCheck" + id).prop("checked", false);
	subjects[id].sel = false
	reloadResults()
}
