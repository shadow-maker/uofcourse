const courseContainers = document.querySelectorAll(".course-container")
const courseItems = document.querySelectorAll(".course-item")

// AJAX for dragging course items

function requestEditCollection(data) {
	$.ajax({
		data: data,
		type: "PUT",
		url: "/api/u/course",
	}).done(function (data) {
		console.log(data);
		if (data.error)
			$("#errorPopup").show()
			$("#errorPopup .message").text(data.error)
	})
}

var oldContainer = null

courseItems.forEach(item => {
	item.addEventListener("dragstart", () => {
		item.classList.add("dragging")
		oldContainer = item.parentElement
	})

	item.addEventListener("dragend", () => {
		item.classList.remove("dragging")
		
		if (oldContainer != item.parentElement)
			requestEditCollection({
				id: item.getAttribute("db-id"),
				collection_id: item.parentElement.getAttribute("db-id")
			})
	})
})

courseContainers.forEach(container => {
	container.addEventListener("dragover", e => {
		e.preventDefault()
		const item = document.querySelector(".dragging")
		container.appendChild(item)
	})
})


// Normal form submission


$(document).on("click", ".course-item", function () {
	if (!this.classList.contains("dragging")) {
		let form = $("#formEditUserCourse")

		let courseId = this.getAttribute("db-id")
		let courseCode = this.querySelector("#code").innerText
		let coursePassed = this.getAttribute("db-passed")
		let collectionId = this.parentElement.getAttribute("db-id")

		form.find("#selectCourse").val(courseId)
		form.find("#selectCoursePlaceholder").val(courseCode)
		form.find("#selectCollection").val(collectionId)

		if (coursePassed == "true") {
			form.find("#selectPassedTrue").prop("checked", true)
			form.find("#selectPassedFalse").prop("checked", false)
		} else if (coursePassed == "false") {
			form.find("#selectPassedTrue").prop("checked", false)
			form.find("#selectPassedFalse").prop("checked", true)
		} else {
			form.find("#selectPassedTrue").prop("checked", false)
			form.find("#selectPassedFalse").prop("checked", false)
		}
	}
});
