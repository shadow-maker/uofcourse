// Code for Edit Tags modal

tagsEdit = {}
tagsDelete = {}
tagsAdd = {}

tagIndex = 0

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
	$("#modalEditTags .tag-items").append(`
		<div id="tag-edit-` + tagIndex +`" class="">
		<div class="inputs row">
			<div class="col-11">
				<div class="input-group">
					<input type="text" class="tag-name form-control" name="name" placeholder="Tag name" aria-label="Tag name">
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
				tagEditDone(() => {
					loadEditTagsModal()
				})
			}
		}

		data = {}
		data.tag_id = $(this).attr("db-id")

		if (data.tag_id && getTagById(data.tag_id)) {
			if ($(this).attr("db-delete") == "true") {
				requestTag("DELETE", data, callback)
			} else if (getTagById(data.tag_id).deletable) {
				data.name = $(this).find(".tag-name").val()
				if (data.name.length > 0 && data.name != getTagById(data.tag_id).name) {
					requestTag("PUT", data, callback)
				}
			}
		} else {
			data.name = $(this).find(".tag-name").val()
			if (data.name.length > 0) {
				data.color = 0
				requestTag("POST", data, callback)
			}	
		}
	})
}

// EXTRA

function getTagById(tagId) {
	for (tag of userTags)
		if (tag.id == tagId)
			return tag
	return null
}

function loadEditTagsModal() {
	$("#modalEditTags .tag-items").empty()
	for (let tag of userTags) {
		$("#modalEditTags .tag-items").append(`
			<div id="tag-edit-` + tagIndex +`" db-id=` + tag.id +` db-delete="false">
				<div class="inputs row">
					<div class="col-11">
						<div class="input-group">
							<input type="text" class="tag-name form-control" name="name" placeholder="Tag name" aria-label="Tag name" value="` + tag.name + `" ` + (tag.deletable ? `` : `readonly`) + `>
						</div>
					</div>
					<div class="col-1 ps-0">
						<button class="btn px-0" type="button" title="Delete tag" ` + (tag.deletable ? `onclick="tagRemove(` + tagIndex +`)"` : `disabled`) + `>
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
	loadEditTagsModal()
})
