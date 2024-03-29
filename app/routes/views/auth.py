from app import db
from app.models import UserLogEvent, User
from app.auth import login_user, logout_user, current_user
from app.forms import formLogin, formSignup
from app.constants import ALLOW_ACCOUNT_CREATION

from app.routes.views import view

from flask import render_template, flash, redirect, request, session
from flask.helpers import url_for


# Routes

@view.route("/signup", methods=["GET", "POST"])
def signup():
	if current_user.is_authenticated:
		flash(f"You are already authenticated!", "success")
		return redirect(url_for("view.home"))

	if not ALLOW_ACCOUNT_CREATION:
		flash(f"Account creation is currently disabled!", "warning")
		return redirect(url_for("view.home"))

	form = formSignup()
	if form.validate_on_submit():
		if User.query.filter_by(username=form.uname.data).first():
			flash(f"User with Username {form.uname.data} already exist. Please sign in.", "danger")
		else:
			user = User(
				form.uname.data,
				form.name.data.strip(),
				form.email.data.strip(),
				form.passw.data,
				form.fac.data
			)
			db.session.add(user)
			db.session.commit()
			user.log(UserLogEvent.AUTH_CREATE_ACCOUNT)
			flash(f"Account created!", "success")
			return redirect(url_for("view.login"))
		return redirect(url_for("view.home"))

	return render_template("signup.html",
		title="Sign Up",
		header="Create Account",
		form=form
	)

@view.route("/login", methods=["GET", "POST"])
def login():
	if current_user.is_authenticated:
		flash(f"You are already authenticated!", "success")
		return redirect(url_for("view.home"))
	form = formLogin()
	if form.validate_on_submit():
		if form.useuname.data:
			user = User.query.filter_by(username=form.uname.data).first()
			using = "username"
		else:
			user = User.query.filter_by(email=form.email.data).first()
			using = "email"
		if user:
			if user.checkPassw(form.passw.data):
				login_user(user, remember=form.remember.data)
				user.log(UserLogEvent.AUTH_LOGIN)
				session["welcome"] = True
				flash(f"Log in successful!", "success")
				nextPage = request.args.get("next")
				return redirect(nextPage if nextPage else url_for("view.home"))
			else:
				flash(f"Incorrect password!", "danger")
		else:
			flash(f"User with {using} {form.uname.data} doesn't exist. Please sign up for an account.", "danger")
	return render_template("login.html",
		title="Log In",
		header="Log In",
		form=form
	)

@view.route("/logout")
def logout():
	if not current_user.is_authenticated:
		return redirect(url_for("view.login"))
	current_user.log(UserLogEvent.AUTH_LOGOUT)
	logout_user()
	flash("Logout successful!", "success")
	return redirect(url_for("view.home"))
