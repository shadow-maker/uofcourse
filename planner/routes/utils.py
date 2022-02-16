from flask import flash, redirect
from flask.helpers import url_for

def redirectLogin():
	flash(f"You need to log in first!", "warning")
	return redirect(url_for("auth.login"))

def redirectNoaccess():
	flash(f"You do not have permission to access this page!", "warning")
	return redirect(url_for("main.viewHome"))