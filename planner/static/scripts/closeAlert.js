function closeAlert(index){
	setTimeout(function(){
		$("#popup" + index).alert("close")
	}.bind(this), 100)
}