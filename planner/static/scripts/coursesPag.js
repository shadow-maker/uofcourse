function switchPage(page) {
	document.getElementById("page").setAttribute("value", String(page))
	document.getElementById("form").submit()
}