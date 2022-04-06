from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, PasswordField, SelectField, SelectMultipleField, SubmitField
#from wtforms.fields.html5 import IntegerRangeField
#from wtforms.widgets.html5 import NumberInput
from wtforms.validators import ValidationError, DataRequired, Email, NumberRange, Length
from planner.models import User, Faculty

from datetime import date

#
# Validation funcs
#

def ucidValidation(form, field):
	if len(str(field.data)) != 8:
		raise ValidationError("UCID must be 8 characters long")

def unameValidation(form, field):
	if len(str(field.data)) < 4:
		raise ValidationError("Username must be at least 4 characters long")
	if len(str(field.data)) > 16:
		raise ValidationError("Username must be at most 16 characters long")

def nameValidation(form, field):
	if len(str(field.data)) > 32:
		raise ValidationError("Name must be less at most 32 characters long")

def passwValidation(form, field):
	if len(str(field.data)) > 64:
		raise ValidationError("Password must be at most 64 characters long")

#
# Forms
#

class loginForm(FlaskForm):
	uname = StringField("Username", validators=[unameValidation])
	passw = PasswordField("Password", validators=[DataRequired()])
	remember = BooleanField("Remember password")
	submit = SubmitField("Log In")

class registerForm(FlaskForm):
	uname = StringField("Username", validators=[DataRequired(), unameValidation])
	name = StringField("Name", validators=[nameValidation])
	email = StringField("Email", validators=[DataRequired(), Email()])
	passw = PasswordField("Password", validators=[DataRequired(), passwValidation])
	fac = SelectField("Faculty", choices=[(f.id, f.name) for f in Faculty.query.all()], validators=[DataRequired()])
	submit = SubmitField("Create account")
