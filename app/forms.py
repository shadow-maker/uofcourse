from app.models import User, Faculty

from flask_wtf import FlaskForm

from wtforms import StringField, TextAreaField, IntegerField, BooleanField, PasswordField, SelectField, SelectMultipleField, SubmitField
#from wtforms.fields.html5 import IntegerRangeField
#from wtforms.widgets.html5 import NumberInput
from wtforms.validators import ValidationError, DataRequired, Email, NumberRange, Length

from datetime import date

import re

SPECIAL_CHARS = re.compile("[@!#$%^&*()<>?/\|}{~:]")

#
# Validation funcs
#

def ucidValidation(form, field):
	if len(str(field.data)) != 8:
		raise ValidationError("UCID must be 8 characters long")

def unameCheck(uname):
	return bool(User.query.filter_by(username=uname).first())

def unameValidation(form, field):
	if " " in field.data:
		raise ValidationError("Username cannot contain spaces")
	if SPECIAL_CHARS.search(field.data):
		raise ValidationError("Username cannot contain special characters")
	if len(str(field.data)) < 4:
		raise ValidationError("Username must be at least 4 characters long")
	if len(str(field.data)) > 16:
		raise ValidationError("Username must be at most 16 characters long")

def unameExists(form, field):
	if not unameCheck(field.data):
		raise ValidationError("Username does not exist")

def unameNew(form, field):
	if unameCheck(field.data):
		raise ValidationError("Username already exists, please choose a new one")

def nameValidation(form, field):
	if len(str(field.data)) > 32:
		raise ValidationError("Name must be less at most 32 characters long")

def passwValidation(form, field):
	if len(str(field.data)) < 6:
		raise ValidationError("Password must be at least 8 characters long")
	if len(str(field.data)) > 64:
		raise ValidationError("Password must be at most 64 characters long")

#
# Forms
#

class formLogin(FlaskForm):
	uname = StringField("Username", validators=[DataRequired(), unameValidation, unameExists])
	passw = PasswordField("Password", validators=[DataRequired()])
	remember = BooleanField("Remember password")
	submit = SubmitField("Log In")


class formSignup(FlaskForm):
	uname = StringField("Username", validators=[DataRequired(), unameValidation, unameNew])
	name = StringField("Name", validators=[nameValidation])
	email = StringField("Email", validators=[DataRequired(), Email()])
	passw = PasswordField("Password", validators=[DataRequired(), passwValidation])
	fac = SelectField("Faculty", choices=[(f.id, f.name) for f in Faculty.query.all()], validators=[DataRequired()])
	submit = SubmitField("Create account")


class formChangePassw(FlaskForm):
	oldPassw = PasswordField("Current password", validators=[DataRequired()])
	newPassw = PasswordField("New password", validators=[DataRequired(), passwValidation])
	submit = SubmitField("Save")


class formContact(FlaskForm):
	email = StringField("Email", validators=[DataRequired(), Email()])
	message = TextAreaField("Message", validators=[DataRequired()])
	submit = SubmitField("Send")
