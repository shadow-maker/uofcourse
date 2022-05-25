//
// GLOBAL VARS
//

var prevData = {}

// Init Page object (defined in pagination.html)
var page = new Page(0, () => {
	requestResults((data) => {
		updateResults(data)
	})
})
