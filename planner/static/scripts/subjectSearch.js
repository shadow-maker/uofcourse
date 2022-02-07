function remSubj(code) {
	$("#subj" + code).remove()
	subjects[code].sel = false // FIXME: sel isn't being set to false when removing the last subject
	$("form").submit()
}
