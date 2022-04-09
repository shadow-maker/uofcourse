from planner import db, loginManager
from planner.models import User
from planner.forms import formLogin, formSignup
from planner.constants import ALLOW_ACCOUNT_CREATION

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
		return redirect(url_for("view.home"))

	if not ALLOW_ACCOUNT_CREATION:
		flash(f"Account creation is currently disabled!", "warning")
		return redirect(url_for("view.home"))

	form = formSignup()
	if form.validate_on_submit():
		if User.query.filter_by(username=form.uname.data).first():
			flash(f"User with Username {form.uname.data} already exist. Please sign in.", "danger")
		else:
			user = User(form.uname.data, form.name.data, form.email.data, form.passw.data, form.fac.data)
			db.session.add(user)
			db.session.commit()
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
		user = User.query.filter_by(username=form.uname.data).first()
		if user:
			if user.checkPassw(form.passw.data):
				login_user(user, remember=form.remember.data)
				flash(f"Log in successful!", "success")
				return redirect(url_for("view.home"))
			else:
				flash(f"Incorrect password!", "danger")
		else:
			flash(f"User with Username {form.uname.data} doesn't exist. Please sign up for an account.", "danger")
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
	return redirect(url_for("view.home"))
