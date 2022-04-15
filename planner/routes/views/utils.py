from flask import flash, redirect
from flask.helpers import url_for

def redirectNoaccess():
	flash(f"You do not have permission to access this page!", "warning")
	return redirect(url_for("view.home"))
