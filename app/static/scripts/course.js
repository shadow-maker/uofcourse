//
// REQUEST FUNCTIONS
//

function requestCourseTags(callback = (response) => {}) {
	if (isAuth)
		$.ajax({
			url: "/api/tags/course/" + course_id,
			method: "GET",
			success: (response) => {callback(response)},
			error: (response) => {
				displayError(response)
			}
		})
}

function toggleTag(tagId) {
	$.ajax({
		url: "/api/tags/course",
		method: "PUT",
		data: {
			course_id: course_id,
			tag_id: tagId
		},
		success: (data) => {
			alert("success", data.success)
			updateTags()
		},
		error: (data) => {
			displayError(data)
		}
	})
}

function addCollection(collectionId) {
	$.ajax({
		url: "/api/users/course",
		method: "POST",
		data: {
			course_id: course_id,
			collection_id: collectionId
		},
		success: (data) => {
			location.reload()
		},
		error: (data) => {
			displayError(data)
		}
	})
}

//
// UPDATE FUNCTIONS
//

function updateTags() {
	const item = $("#tags")
	item.find(".loading").show()

	// Add dropdown items

	const dropdown = item.find(".tags-dropdown")
	dropdown.empty()

	for (let tag of userTags) {
		dropdown.append(`
			<li class="tags-dropdown-item" db-id="` + tag.id +`">
				<a class="dropdown-item px-2 py-1" onclick="toggleTag(` + tag.id + `)" style="cursor: pointer;">
					<i class="bi-check"></i>
					<small>` + tag.name +`</small>
				</a>
			</li>
		`)
	}

	dropdown.append(`
		<li><hr class="dropdown-divider my-1"></li>
		<li><a class="dropdown-item px-2 p-y1" href="" data-bs-toggle="modal" data-bs-target="#modalEditTags" onclick="loadEditTagsModal()">
			<i class="bi-pencil-square"></i>
			<small>Edit tags</small>
		</a></li>
	`)

	// Request course tags and add selected tags

	let icon = ""
	requestCourseTags((response) => {
		item.find(".tags-dropdown").children(".tags-dropdown-item").each(function () {
			$(this).find(".bi-check").addClass("invisible")
		})

		const container = item.find(".tags-selected")
		container.empty()
		for (tag of response.tags) {

			if (tag.emoji)
				icon = "&#" + tag.emoji + " "
			else
				icon = "<i class='bi-circle-fill' style='color: #" + tag.color_hex +";'></i> "

			container.append(`
				<span class="course-tag btn badge btn-secondary px-1" title="`+ tag.name + `" style="cursor: pointer;" db-id="` + tag.id + `" onclick="toggleTag(` + tag.id+ `)">
					` + icon + tag.name + `
				</span>
			`)

			item.find(".tags-dropdown").children(".tags-dropdown-item").each(function () {
				if($(this).attr("db-id") == tag.id)
					$(this).find(".bi-check").removeClass("invisible")
			})
		}
	})

	item.find(".loading").hide()
}

//
// DOCUMENT READY
//

$(document).ready(() => {
	tagsInit(() => {
		updateTags()
	})
})
