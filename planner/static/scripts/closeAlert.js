function closeAlert(index){
	setTimeout(function(){
		$("#popup" + index).addClass("leave")
		setTimeout(() => {
			$("#popup" + index).hide()
		}, 300)
	}.bind(this), 100)
}