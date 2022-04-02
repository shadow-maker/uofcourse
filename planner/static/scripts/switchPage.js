class Page {
	constructor(pages, callback = () => {}) {
		this.current = 1
		this.total = pages
		this.callback = callback
	}

	switch(_page) {
		if (_page > 0 && _page <= this.total) {
			this.current = _page
			this.callback()
		}
	}
	
	prev() {
		if (this.current > 1)
			this.switch(this.current - 1)
	}

	next() {
		if (this.current < this.total)
			this.switch(this.current + 1)
	}

	first() {
		this.switch(1)
	}

	last() {
		this.switch(this.total)
	}
}
