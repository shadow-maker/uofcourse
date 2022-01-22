function switchPage(page) {
	$("#page").attr("value", String(page))
	$("#form").submit()
}