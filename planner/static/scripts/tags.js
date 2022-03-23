// Code for Edit Tags modal

var tagIndex = 0

function colorToHex(color) {
	return ("000000" + color.toString(16)).slice(-6)
}

// REQUEST FUNCS

function requestTag(method, data, suc) {
	$.ajax({
		url: "/api/tags",
		method: method,
		data: data,
		success: (data) => {suc(data)},
		error: (data) => {
			alert("danger", data.responseJSON.error)
		}
	})
}

// ONCLICK FUNCS

function addTag() {
	const color = Object.keys(colors)[Math.floor(Math.random() * Object.keys(colors).length)]
	$("#modalEditTags .tag-items").append(`
		<div id="tag-edit-` + tagIndex +`" class="">
		<div class="inputs row">
			<div class="col-11">
				<div class="input-group">
					<span class="tag-color-indicator input-group-text" style="color: #` + colorToHex(colors[color]) + `;">
						<i class="bi-circle-fill"></i>
					</span>
					<select class="tag-color form-select" name="color" onchange="tagUpdateColor(` + tagIndex +`)" >
						` + colorOptions(colors[color]) + `
					</select>
					<input type="text" class="tag-name form-control w-25" name="name" placeholder="Tag name" aria-label="Tag name">
				</div>
			</div>
			<div class="col-1 ps-0">
				<button class="btn px-0" type="button" title="Delete tag" onclick="tagDelete(` + tagIndex +`)">
					<i class="h5 bi-trash text-danger"></i>
				</button>
			</div>
		</div>
		<hr class="my-3">
		</div>
	`)
	tagIndex++
}

function tagDelete(index) {
	$("#tag-edit-" + index).remove()
}

function tagRemove(index) {
	$("#tag-edit-" + index).attr("db-delete", "true")
	$("#tag-edit-" + index + " .inputs").hide()
	$("#tag-edit-" + index + " .deleted").show()
}

function tagUndoRemove(index) {
	$("#tag-edit-" + index).attr("db-delete", "false")
	$("#tag-edit-" + index + " .inputs").show()
	$("#tag-edit-" + index + " .deleted").hide()
}

function tagUpdateColor(index) {
	const item = $("#tag-edit-" + index)
	item.find(".tag-color-indicator").css("color", "#" +  colorToHex(parseInt(item.find(".tag-color").val())))
}

function tagExecuteChanges() {
	$("#modalEditTags").modal("hide")
	var data = {}
	var callback = (data) => {
		if (data.success)
			alert("success", data.success)
	}

	$("#modalEditTags .tag-items").children().each(function(i) {
		if (i == $("#modalEditTags .tag-items").length - 1) {
			callback = (data) => {
				if (data.success)
					alert("success", data.success)
				requestTag("GET", {}, (data) => {
					userTags = data.tags
					if (typeof tagEditDone !== "undefined")
						tagEditDone()	
				})
			}
		}

		data = {}
		data.tag_id = $(this).attr("db-id")

		var existing = null
	
		for (let tag of userTags)
			if (tag.id == data.tag_id) {
				existing =  tag
				break
			}

		if (existing) { // Existing tag
			if ($(this).attr("db-delete") == "true") { // Delete tag
				requestTag("DELETE", data, callback)
			} else if (existing.deletable) { // Update tag
				data.name = $(this).find(".tag-name").val()
				data.color = parseInt($(this).find(".tag-color").val())
				if (data.name.length > 0 && (data.name != existing.name || data.color != existing.color))
					requestTag("PUT", data, callback)
			}
		} else { // New tag
			data.name = $(this).find(".tag-name").val()
			data.color = parseInt($(this).find(".tag-color").val())
			if (data.name.length > 0)
				requestTag("POST", data, callback)
		}
	})
}

// EXTRA

function colorOptions(tagColor) {
	var html = ""

	var colorFound = false

	for (let color in colors) {
		if (colors[color] == tagColor)
			colorFound = true
	
		html += `
			<option value='` + colors[color] +`' `  + (colors[color] == tagColor ? `selected` : ``) + `>
				` + color.charAt(0).toUpperCase() + color.slice(1) +`
			</option>
		`
	}

	if (!colorFound) {
		html = `
			<option value='` + tagColor +`' selected>
				#` + colorToHex(tagColor) +`
			</option>
		` + html
	}

	return html
}

function loadEditTagsModal() {
	tagIndex = 0

	$("#modalEditTags .tag-items").empty()
	for (let tag of userTags) {
		$("#modalEditTags .tag-items").append(`
			<div id="tag-edit-` + tagIndex +`" db-id=` + tag.id +` db-delete="false">
				<div class="inputs row">
					<div class="col-11">
						<div class="input-group">
							<span class="tag-color-indicator input-group-text" style="color: #` + colorToHex(tag.color) + `;">
								<i class="bi-circle-fill"></i>
							</span>
							<select class="tag-color form-select" name="color" onchange="tagUpdateColor(` + tagIndex +`)" ` + (tag.deletable ? `` : `disabled title="Tag cannot be edited"`) + `>
								` + colorOptions(tag.color) + `
							</select>
							<input type="text" class="tag-name form-control w-25" name="name" placeholder="Tag name" aria-label="Tag name" value="` + tag.name + `" ` + (tag.deletable ? `` : `readonly title="Tag cannot be edited"`) + `>
						</div>
					</div>
					<div class="col-1 ps-0">
						<button class="btn px-0" type="button" ` + (tag.deletable ? `title="Delete tag" onclick="tagRemove(` + tagIndex +`)"` : `disabled title="Tag cannot be deleted"`) + `>
							<i class="h5 bi-trash text-danger"></i>
						</button>
					</div>
				</div>
				<div class="deleted row">
					<div class="col-11">
						<div class="input-group">
							<input type="text" class="form-control fst-italic" placeholder="Tag deleted" aria-label="Tag deleted" value="Deleted" disabled>
						</div>
					</div>
					<div class="col-1 ps-0">
						<button class="btn px-0" type="button" title="Undo delete tag" onclick="tagUndoRemove(` + tagIndex +`)">
							<i class="h5 bi-arrow-counterclockwise"></i>
						</button>
					</div>
				</div>
				<hr class="my-3">
			</div>
		`)
		$("#tag-edit-" + tagIndex + " .deleted").hide()
		tagIndex++
	}
}

// DOCUMENT READY

$(document).ready(() => {
	if (typeof isAuth === "undefined" || !isAuth)
		userTags = []

	if (typeof userTags === "undefined") { // If userTags was not passed from the server on template load
		requestTag("GET", {}, (data) => {
			userTags = data.tags
			if (typeof tagsInit !== "undefined")
				tagsInit()
			loadEditTagsModal()
		})
	} else {
		if (typeof tagsInit !== "undefined")
			tagsInit()
		loadEditTagsModal()
	}
})
