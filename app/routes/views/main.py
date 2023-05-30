from app import app, jinja, ifttt
from app.auth import current_user
from app.models import Term
from app.forms import formContact
from app.routes.views import view
from app.constants import MESSAGES_TIMEOUT
from app.localdt import utc, local

from flask import render_template, flash, redirect, request, session
from flask.helpers import url_for

from markdown import markdown
import os
import json


@view.route("/home")
@view.route("/")
def home():
	term = Term.getCurrent()
	if not term:
		term = Term.getNext()
	courses = []
	if term and current_user.is_authenticated:
		for collection in current_user.collections:
			if collection.term_id == term.id:
				courses = sorted(collection.collectionCourses, key=lambda c: c.course.code)
				break

	return render_template("index.html",
		header = "UofC Course Planner",
		welcome = "welcome" in session and session["welcome"],
		term = term,
		collectionCourses = courses,
		today = local.date()
	)


@view.route("/about")
def about():
	return render_template("about.html",
		title = "About",
		header = "About UofCourse",
		headerIcon = "info-square"
	)

@view.route("/announcements")
def announcements():
	return render_template("announcements.html",
		title = "Announcements",
		header = "Announcements",
		headerIcon = "bell-fill",
		description = "Relevant changes and modifications performed on the website.",
		announcement_id = request.args.get("id"),
		sortOptions = [
			{"label": "Datetime", "value": ["datetime", "title"]},
			{"label": "Title", "value": ["title", "datetime"]},
		]
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
	html = html.replace("<h4", "<h4 class='mt-3'")
	html = html.replace("<table", "<table class='table table-sm'")
	html = html.replace("<blockquote", "<blockquote title='Copy endpoint' class='alert alert-secondary p-2 d-flex justify-content-between fs-5'")

	return render_template("api.html",
		title = "API",
		header = "API Documentation",
		headerIcon = "braces-asterisk",
		description = "UofCourse API Documentation - Easily get course specific data within your program.",
		html = html
	)


@view.route("/playground")
def apiPlayground():
	return render_template("apiPlayground.html",
		title = "API Playground",
		header = "API Playground",
		headerIcon = "braces-asterisk",
		description = "Test out the UofCourse API endpoints in real time.",
		baseURLFull = url_for('view.api', _external=True),
		baseURL = url_for('view.api', _external=True).replace("https://", "").replace("http://", "").replace("www.", "")
	)


@view.route("/contact", methods=["GET", "POST"])
def contact():
	form = formContact()
	if form.validate_on_submit():
		# Check if another message was sent recently
		last = session["last_message"] if "last_message" in session else None
		if last and (utc.now() - last).seconds < MESSAGES_TIMEOUT:
			flash(f"You already sent a message! Please wait {MESSAGES_TIMEOUT - (utc.now() - last).seconds} seconds to send another message.", "warning")
			return redirect(url_for("view.contact"))

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
			session["last_message"] = utc.now()
			flash("Message received!", "success")
		return redirect(url_for("view.contact"))

	return render_template("contact.html",
		title = "Contact",
		header = "Contact admins",
		headerIcon = "chat-text-fill",
		form = form
	)


@view.route("/changelog")
def changelog():
	try:
		with open(os.path.join(app.static_folder, "changelog.json"), "r") as file:
			data = json.load(file)
	except:
		data = {}
		flash("Could not load the changelog", "danger")

	return render_template("changelog.html",
		title = "Changelog",
		header = "Changelog",
		headerIcon = "bug-fill",
		changelog = data
	)


@view.route("/counter")
def counter():
	return render_template("counter.html",
		title = "User Counter",
		header = "Real Time User Counter",
		headerIcon = "people-fill"
	)
