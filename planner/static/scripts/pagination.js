class Page {
	constructor(pages, callback = () => {}) {
		this.current = 1
		this.total = pages
		this.callback = callback
	}

	updateNav() {
		$("#pageNav .pageSelector").remove()
		if (this.total > 15) {
			$("#pageNav .pageEllipsis").show()
		} else {
			$("#pageNav .pageEllipsis").hide()
			for (let p = this.total; p > 0; p--) {
				$("#pageNav ul li:eq(0)").after(`
					<li class="pageSelector page-item ` + ((p == this.current) ? `active` : ``) + `"
					onclick="page.switch(` + ((p == this.current) ? -1 : p) + `)" style="cursor: pointer;">
						<a class="page-link">` + p +`</a>
					</li>
				`)
			}
		}

		$("#numPage").text(this.current)
		$("#numPages").text(this.total)
	}

	switch(_page) {
		if (_page > 0 && _page <= this.total) {
			this.current = _page
			this.callback()
			updateNav()
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
