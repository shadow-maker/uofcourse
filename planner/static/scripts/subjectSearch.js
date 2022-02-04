function remSubj(id) {
	$("#subj" + id).remove()
	subjects[id].sel = false // FIXME: sel isn't being set to false when removing the last subject
	$("form").submit()
}
