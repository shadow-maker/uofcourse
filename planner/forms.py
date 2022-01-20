from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, PasswordField, SelectField, SelectMultipleField, SubmitField
#from wtforms.fields.html5 import IntegerRangeField
#from wtforms.widgets.html5 import NumberInput
from wtforms.validators import ValidationError, DataRequired, Email, NumberRange, Length
from planner.models import User, Faculty
from planner.queryUtils import *

from datetime import date

#
# Validation funcs
#

def ucidValidation(form, field):
	if len(str(field.data)) != 8:
		raise ValidationError("UCID must be 8 characters long")

def nameValidation(form, field):
	if len(str(field.data)) > 32:
		raise ValidationError("Name must be less than 32 characters long")

def passwValidation(form, field):
	if len(str(field.data)) > 32:
		raise ValidationError("Password must be less than 64 characters long")

def entryYearValidation(form, field):
	if field.data < 1966 or field.data > date.today().year:
		raise ValidationError("Invalid year of entry")

#
# Forms
#

class loginForm(FlaskForm):
	ucid = IntegerField("UCID", validators=[ucidValidation])
	passw = PasswordField("Password", validators=[DataRequired()])
	remember = BooleanField("Remember password")
	submit = SubmitField("Sign In")

class registerForm(FlaskForm):
	ucid = IntegerField("UCID", validators=[DataRequired(), ucidValidation])
	name = StringField("Name", validators=[nameValidation])
	email = StringField("Email", validators=[DataRequired(), Email()])
	passw = PasswordField("Password", validators=[DataRequired(), passwValidation])
	fac = SelectField("Faculty", choices=[(f.id, f.name) for f in Faculty.query.all()], validators=[DataRequired()])
	entry = IntegerField("Year of entry", validators=[entryYearValidation])
	submit = SubmitField("Create account")
