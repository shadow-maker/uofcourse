from planner import db, bcrypt, loginManager
from planner.forms import *
from planner.queryUtils import *
from planner.constants import *

from planner.routes.views import view

from flask import render_template, flash, redirect
from flask.helpers import url_for
from flask_login import login_user, logout_user, current_user


# Login utils

@loginManager.user_loader
def loadUser(uId):
	return User.query.get(int(uId))


# Routes

@view.route("/signup", methods=["GET", "POST"])
def signup():
	if current_user.is_authenticated:
		flash(f"You are already authenticated!", "success")
		return redirect(url_for("main.viewHome"))

	if not ALLOW_ACCOUNT_CREATION:
		flash(f"Account creation is currently disabled!", "warning")
		return redirect(url_for("main.viewHome"))

	form = registerForm()
	if form.validate_on_submit():
		if userExists(form.ucid.data):
			flash(f"User with UCID {form.ucid.data} already exist. Please sign in.", "danger")
		else:
			user = User(form.ucid.data, form.email.data, form.passw.data, form.fac.data)
			if form.name.data:
				user.name = form.name.data
			if form.entry.data:
				user.entryYear = form.entry.data
			db.session.add(user)
			db.session.commit()
			flash(f"Account created!", "success")
			return redirect(url_for("view.login"))
		return redirect(url_for("main.viewHome"))

	return render_template("signup.html",
		title="Sign Up",
		header="Create Account",
		form=form
	)

@view.route("/login", methods=["GET", "POST"])
def login():
	if current_user.is_authenticated:
		flash(f"You are already authenticated!", "success")
		return redirect(url_for("main.viewHome"))
	form = loginForm()
	if form.validate_on_submit():
		if not userExists(form.ucid.data):
			flash(f"User with UCID {form.ucid.data} doesn't exist. Please sign up for an account.", "danger")
		else:
			user = getById(User, form.ucid.data)
			if bcrypt.check_password_hash(user.passw, form.passw.data):
				login_user(user, remember=form.remember.data)
				flash(f"Log in successful! (#{user.id})", "success")
				return redirect(url_for("main.viewHome"))
			else:
				flash(f"Incorrect password!", "danger")
	return render_template("login.html",
		title="Log In",
		header="Log In",
		form=form
	)

@view.route("/logout")
def logout():
	if not current_user.is_authenticated:
		return redirect(url_for("view.logout"))
	logout_user()
	return redirect(url_for("main.viewHome"))