function ajax(method, endpoint, data, success=()=>{}, error=displayError, complete=()=>{}) {
	if (method.toUpperCase() != "GET")
		data = JSON.stringify(data)
	$.ajax({
		method: method,
		url: "/api/" + endpoint,
		headers: {"AJAX-TOKEN": AJAX_TOKEN},
		data: data,
		traditional: true,
		dataType: "json",
		contentType: "application/json",
		success: success,
		error: error,
		complete: complete
	})
}