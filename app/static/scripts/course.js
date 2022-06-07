//
// REQUEST FUNCTIONS
//

function requestCourseTagsCustom(callback) {
	if (isAuth)
		requestCourseTags(course_id, callback)
}

function toggleTag(tagId) {
	requestTag("/" + tagId + "/course/" + course_id, "PUT", {}, (data) => {
		alert("success", data.success)
		updateTags()
	})
}

function addCollection(collectionId) {
	$.ajax({
		url: "/api/me/course",
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
				<a class="dropdown-item px-2 py-1" onclick="toggleTag(` + tag.id + `)">
					<i class="bi-check"></i>
					<small>` + tag.name +`</small>
				</a>
			</li>
		`)
	}

	dropdown.append(`
		<li><hr class="dropdown-divider my-1"></li>
		<li><a class="dropdown-item px-2 p-y1" href="" data-bs-toggle="modal" data-bs-target="#modalEditTags">
			<i class="bi-pencil-square"></i>
			<small>Edit tags</small>
		</a></li>
	`)

	// Request course tags and add selected tags

	let icon = ""
	requestCourseTagsCustom((response) => {
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
	tagsInit(updateTags)
})
