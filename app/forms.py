from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, TextAreaField, DecimalField, IntegerField, RadioField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
from datetime import datetime, timedelta
from app.models import Student, Loan

class RegistrationForm(FlaskForm): 
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
	email = StringField('Email', validators=[DataRequired()])
	dob = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])
	phone = StringField('Phone Number', validators=[DataRequired(), Length(max=11)])
	address = TextAreaField('Address', validators=[DataRequired(), Length(max=200)])
	height = DecimalField('Height (cm)', validators=[DataRequired()])
	weight = DecimalField('Weight (kgs)', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Sign Up')

	def validate_dob(self, dob):
          today = datetime.now().date()
          min_age_date = today - timedelta(days=18*365)
          max_birth_date = today - timedelta(days=365*120)
          if self.dob.data > min_age_date or self.dob.data < max_birth_date or self.dob.data > today:
            return False
          return True

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')
    
class AddStudentForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    firstname = StringField('Firstname')
    lastname = StringField('Lastname', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Add Student')

    def validate_username(self, username):
        if Student.query.filter_by(username=username.data).first():
            raise ValidationError('This username is already taken. Please choose another')

    def validate_email(self, email):
        if Student.query.filter_by(email=email.data).first():
            raise ValidationError('This email address is already registered. Please choose another')
        
class BorrowForm(FlaskForm):
    student_id = StringField('Student ID', validators=[DataRequired()])
    device_id = StringField('Device ID', validators=[DataRequired()])
    submit = SubmitField('Borrow')
    
    def validate_loan(self, student_id): # see what happens if this is removed, message won't flash at the top? 
        existing_loan = Loan.query.filter_by(student_id=student_id.data, returndatetime=None).first()
        if existing_loan:
            raise ValidationError('You already have a device on loan. Please return it before borrowing another device.')

class ReturnForm(FlaskForm):
    student_id = StringField('Student ID', validators=[DataRequired()])
    device_id = StringField('Device ID', validators=[DataRequired()])
    submit = SubmitField('Return Device')
    
class RemoveStudentForm(FlaskForm):
    username = StringField('Student Username', validators=[DataRequired()])
    email = StringField('Student Email', validators=[DataRequired(), Email()])
    admin_key = StringField('Admin Key', validators=[DataRequired()])
    submit = SubmitField('Confirm Deletion')

class ReportForm(FlaskForm):
    student_id = StringField('Student ID')
    device_id = StringField('Device ID')
    submit = SubmitField('Get Loan Information')


class DeactivateStudentForm(FlaskForm):
    student_id = IntegerField('Student ID', validators=[DataRequired()])
    submit = SubmitField('Deactivate Student')

    def validate_student_id(self, student_id):
        if not Student.query.get(student_id.data):
            raise ValidationError(
            	'There is no student with this id in the system')
        if not Student.query.get(student_id.data).active:
            raise ValidationError('This student is already deactivated')

class SearchForm(FlaskForm):
    search_query = StringField('', validators=[DataRequired()])
    choice = RadioField('', choices=[('student', 'student'), ('device', 'device')])
    submit = SubmitField('Submit')