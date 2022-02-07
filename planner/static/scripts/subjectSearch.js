$(document).on("click", ".subjItem", function () {
	subjects[this.getAttribute("code")].sel = false
	this.remove()
	$("form").submit()
});
