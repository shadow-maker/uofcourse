from planner import changelog as change
from planner.models import Role
from planner.forms import contactForm
from planner.routes.views import view
from planner.utils import sendMessage

from flask import render_template, flash
from flask_login import current_user
from flask_mail import Message


@view.route("/home")
@view.route("/")
def home():
	return render_template("index.html",
		header = "UofC Course Planner"
	)


@view.route("/about")
def about():
	return render_template("about.html",
		title = "About",
		header = "About UofCourse"
	)


@view.route("/api")
def api():
	return render_template("api.html",
		title = "API",
		header = "Coming soon..."
	)


@view.route("/contact", methods=["GET", "POST"])
def contact():
	form = contactForm()
	if form.validate_on_submit():
		if current_user.is_authenticated:
			body = "A USER HAS SENT A MESSAGE\n\n"
			body += f"NAME: {current_user.name}\n"
			body += f"USERNAME: {current_user.username}\n"
			body += f"EMAIL: {current_user.email}\n"
		else:
			body = "A (GUEST) USER HAS SENT A MESSAGE\n\n"
			body += f"EMAIL: {form.email.data}\n"
		body += f"\n--- MESSAGE ---\n{form.message.data}\n---\n"
		try:
			recipients = [u.email for u in Role.query.filter_by(name="admin").first().users]
			sendMessage(recipients, f"New message received", body)
		except:
			flash("An error occured while sending the message.", "danger")
		else:
			flash("Message received!", "success")

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
