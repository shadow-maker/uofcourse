const courseContainers = document.querySelectorAll(".course-container")
const courseItems = document.querySelectorAll(".course-item")

function requestEditCollection(courseId, collectionId) {
	$.ajax({
		data: {
			id: courseId,
			collection_id: collectionId,
		},
		type: "PUT",
		url: "/api/u/course",
	}).done(function (data) {
		console.log(data);
		if (data.error) {
			$("#errorPopup").show();
			$("#errorPopup .message").text(data.error);
		}
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
		if (oldContainer != item.parentElement) {
			requestEditCollection(item.getAttribute("db-id"), item.parentElement.getAttribute("db-id"))
		}
	})
})

courseContainers.forEach(container => {
	container.addEventListener("dragover", e => {
		e.preventDefault()
		const item = document.querySelector(".dragging")
		container.appendChild(item)
	})
})


$(document).on("click", ".course-item", function () {
	if (!this.classList.contains("dragging")) {
		let form = $("#formEditUserCourse")

		let courseId = this.getAttribute("db-id")
		let courseCode = this.querySelector("#code").innerText
		let collectionId = this.parentElement.getAttribute("db-id")

		form.find("#selectedCourse").val(courseId)
		form.find("#selectedCoursePlaceholder").val(courseCode)
		form.find("#selectedCollection").val(collectionId)
	}
});
