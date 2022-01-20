const courseContainers = document.querySelectorAll(".course-container")
const courseItems = document.querySelectorAll(".course-item")

console.log(courseContainers)
console.log(courseItems)

courseItems.forEach(item => {
	item.addEventListener("dragstart", () => {
		item.classList.add("dragging")
	})

	item.addEventListener("dragend", () => {
		item.classList.remove("dragging")
	})
})

courseContainers.forEach(container => {
	container.addEventListener("dragover", e => {
		e.preventDefault()
		const item = document.querySelector(".dragging")
		container.appendChild(item)
	})
})