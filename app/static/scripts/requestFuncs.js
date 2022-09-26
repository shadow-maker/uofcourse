function ajax(method, endpoint, data, success=()=>{}, error=displayError, complete=()=>{}) {
	if (method.toUpperCase() != "GET")
		data = JSON.stringify(data)
	$.ajax({
		method: method,
		url: "/api/" + endpoint,
		data: data,
		traditional: true,
		dataType: "json",
		contentType: "application/json",
		success: success,
		error: error,
		complete: complete
	})
}