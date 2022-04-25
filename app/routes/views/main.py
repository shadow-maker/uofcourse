from app import app, jinja, ifttt
from app import changelog as change
from app.auth import current_user
from app.forms import formContact
from app.routes.views import view
from app.models import utils

from flask import render_template, flash, redirect, request, session
from flask.helpers import url_for

from datetime import date
from markdown import markdown
import os


@view.route("/home")
@view.route("/")
def home():
	if "welcome" in session:
		print(session["welcome"])
	term = utils.getCurrentTerm()
	if not term:
		term = utils.getNextTerm()
	courses = []
	if term and current_user.is_authenticated:
		for collection in current_user.collections:
			if collection.term_id == term.id:
				courses = sorted(collection.userCourses, key=lambda c: c.course.code)
				break

	return render_template("index.html",
		header = "UofC Course Planner",
		welcome = "welcome" in session and session["welcome"],
		term = term,
		userCourses = courses,
		today = date.today()
	)


@view.route("/about")
def about():
	return render_template("about.html",
		title = "About",
		header = "About UofCourse"
	)


@view.route("/api")
def api():
	# Create jinja2 template from api docs markdown file
	with open(os.path.join(app.static_folder, "api.md"), "r", encoding="utf-8") as file:
		template = jinja.from_string(file.read())

	# Process template with variables
	processed = template.render(
		url_for = url_for
	)

	# Convert markdown to html
	html = markdown(processed, extensions=["attr_list", "tables", "fenced_code"])
	parts = html.partition("h2")
	html = parts[0] + parts[1] + parts[2].replace("h2", "h2 class='mt-5'")
	html = html.replace("<h3", "<h3 class='mt-4'")
	html = html.replace("h4", "h4 class='mt-3'")
	html = html.replace("<table", "<table class='table table-sm'")
	html = html.replace("<blockquote", "<blockquote title='Copy endpoint' class='alert alert-secondary p-2 d-flex justify-content-between fs-5'")

	return render_template("api.html",
		title = "API",
		header = "API Documentation",
		description = "UofCourse API Documentation - Easily get course specific data within your program.",
		html = html
	)


@view.route("/contact", methods=["GET", "POST"])
def contact():
	form = formContact()
	if form.validate_on_submit():
		# Format message body
		if current_user.is_authenticated:
			body = "A USER HAS SENT A MESSAGE\n\n"
			body += f"NAME: {current_user.name}\n"
			body += f"USERNAME: {current_user.username}\n"
			body += f"EMAIL: {current_user.email}\n"
		else:
			body = "A (GUEST) USER HAS SENT A MESSAGE\n\n"
			body += f"EMAIL: {form.email.data}\n"
		ip = request.headers["X-Real-IP"] if "X-Real-IP" in request.headers else request.remote_addr
		body += f"IP ADDRESS: {ip}\n"
		body += f"\n--- MESSAGE ---\n{form.message.data}\n---\n"

		# Send message to IFTTT webhook
		try:
			r = ifttt.message(body)
			if r.status_code != 200:
				raise Exception
		except Exception:
			flash("An error occured while sending the message.", "danger")
		else:
			flash("Message received!", "success")
		return redirect(url_for("view.contact"))

	return render_template("contact.html",
		title = "Contact",
		header = "Contact admins",
		form = form
	)


@view.route("/changelog")
def changelog():
	return render_template("changelog.html",
		title = "Changelog",
		header = "Changelog",
		changelog = change
	)
