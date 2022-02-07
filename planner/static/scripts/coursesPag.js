function switchPage(_page) {
	if (_page > 0) {
		page = parseInt(_page)
		$("form").submit()
	}
}

function switchPagePrev() {
	if (page > 1)
		switchPage(page - 1)
}

function switchPageNext() {
	if (page < pages)
		switchPage(page + 1)
}