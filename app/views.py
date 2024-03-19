from flask import render_template, redirect, url_for, flash, request
from app import app, db
from app.forms import RegistrationForm, BorrowForm, AddStudentForm, ReturnForm, LoginForm, RemoveStudentForm, ReportForm, DeactivateStudentForm, SearchForm
from app.models import Student, Loan, Device, User
from datetime import datetime
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from flask_login import logout_user, login_required, current_user, login_user
from urllib.parse import urlsplit

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(
                username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        flash(f'Login for {form.username.data}', 'success')
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():

        if not form.validate_dob(form.dob):
            flash('Please enter a valid date of birth.')
            return render_template('registration.html', title="Register", form=form)
        
        flash(f'Registration for {form.username.data} received, login to continue.', 'success') # return to login after successfully registering
        return redirect(url_for('login'))
    return render_template('registration.html', title="Register", form=form)

@app.route('/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    form = AddStudentForm()
    if form.validate_on_submit():
        new_student = Student(username=form.username.data, firstname=form.firstname.data,
                              lastname=form.lastname.data, email=form.email.data)
        db.session.add(new_student)
        try:
            db.session.commit()
            flash(f'New Student, {form.username.data} ({form.email.data}) successfully added.', 'success')
            return redirect(url_for('index'))
        except:
            db.session.rollback()
            if Student.query.filter_by(username=form.username.data).first():
                form.username.errors.append('This username is already taken. Please choose another')
            if Student.query.filter_by(email=form.email.data).first():
                form.email.errors.append('This email address is already registered. Please choose another')
    return render_template('add_student.html', title='Add Student', form=form)

@app.route("/borrow", methods=["GET", "POST"])
@login_required
def borrow():
    form = BorrowForm()
    if form.validate_on_submit():
        # check if student has already taken out a loan
        existing_loan = Loan.query.filter_by(student_id=form.student_id.data, returndatetime=None).first()
        if existing_loan:
            flash('You already have a device on loan. Please return it before borrowing another device.', 'warning') # flash shows at top of page
            
        # check if student is registered 
        elif not Student.query.filter(Student.student_id == form.student_id.data).first():
            form.student_id.errors.append("Student is not registered.") # with this append method it shows next to the form
            
        # check if item is already being loaned 
        elif Loan.query.filter(Loan.device_id == form.device_id.data).first().returndatetime is None:
            form.device_id.errors.append("Device is already out for loan.")
        
        # if everything is okay then new loan added to database 
        else:
            new_loan = Loan(student_id=form.student_id.data, device_id=form.device_id.data, borrowdatetime=datetime.now())   
            db.session.add(new_loan)
            try:
                db.session.commit()
                flash('You have succesfully loaned this device.', 'success') # success is the alert catergory not part of the string 
                return redirect(url_for('index'))
            except:
                db.session.rollback()
                if Loan.query.filter_by(student_id=form.student_id.data, returndatetime=None).first():
                    form.student_id.errors.append('You already have a device on loan. Please return it before borrowing another device.', 'warning')
    return render_template("borrow.html", form=form)

@app.route("/return_loan", methods=['GET', 'POST'])
@login_required
def return_loan():
    form = ReturnForm()
    if form.validate_on_submit():
        # check to see if student id has device attached to it 
        try:
            # query for the loan record that matches student and device id 
            existing_loan = Loan.query.filter_by(student_id=form.student_id.data, device_id=form.device_id.data, returndatetime=None).first()
            
            if existing_loan:
                existing_loan.returndatetime = datetime.now()
                db.session.commit()
                flash(f'Device: {form.device_id.data} successfully returned', 'success')
                return redirect(url_for('index'))
            else:
                flash(f'No matching loan record found for the provided student ID and device ID.', 'info')
        except:
            db.session.rollback()
            
    return render_template("return_loan.html", form=form)

@app.route('/remove_student', methods=['GET', 'POST', 'DELETE'])
@login_required
def remove_student():
    form = RemoveStudentForm()
    
    if form.validate_on_submit():
        username = form.username.data.strip() # remove any trailing white space that may be entered when creating the username 
        email = form.email.data.strip()
        student = Student.query.filter_by(username=username, email=email).first()
        if student and form.admin_key.data == "sillybilly":
            try:
                # delete associated loan records first
                Loan.query.filter_by(student_id=student.student_id).delete() # have to delete loans before deleting student 
                # then delete the student
                db.session.delete(student)
                db.session.commit()
                flash(f'Student {student.username} deleted successfully', 'success')
                return redirect(url_for('index'))
            except IntegrityError as e:
                db.session.rollback()
                print("Error occurred during deletion:", str(e))
                flash('An error occurred while deleting the student', 'error')
        elif not student:
            flash(f'Student not found.', 'danger')
        else:
            flash(f'Incorrect admin key.', 'warning')

    return render_template('remove_student.html', title='Remove Student', form=form)

@app.route('/reports', methods=['GET', 'POST'])
@login_required
def reports():
    form = ReportForm()
    loan = None
    student = None
    
    if form.validate_on_submit():
        student = Student.query.filter_by(student_id=form.student_id.data).first()
        
        loan = Loan.query.filter_by(device_id=form.device_id.data).all()

    return render_template('reports.html', title="Reports", form=form, student_data=student, loan_data=loan)


@app.route('/deactivate', methods=['GET', 'POST'])
@login_required
def deactivate():
    form = DeactivateStudentForm()

    if form.validate_on_submit():
        id = form.student_id.data

        try:
            student = Student.query.filter_by(student_id=id).first()
            student.active = False
            db.session.commit()
            flash(f'Student #{id} deactivated', 'success')
            return redirect(url_for('index'))
        except:
            db.session.rollback()

    return render_template('deactivate.html', form=form)


@app.route('/display_students')
@login_required
def display_students():

    students = Student.query.all()

    return render_template('view_students.html', students=students)


@app.route('/search/', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    
    if form.validate_on_submit():
        if form.choice.data == 'student':
            result = Student.query.filter(or_(Student.firstname.contains(form.search_query.data), Student.lastname.contains(
                form.search_query.data), Student.username.contains(form.search_query.data), Student.email.contains(form.search_query.data))).all()
        
        elif form.choice.data == 'device':
            result = Device.query.filter(Device.device_type.contains(form.search_query.data)).all()
            
        if len(result) == 0:
            result = ['No results found']
        
        return render_template('search.html', result=result, form=form)
        
    return render_template('search.html', result=None,form=form)

@app.route("/important_information")
def important_information():
    return render_template("important_information.html")

@app.route("/library_announcements")
def library_announcements():
    return render_template("library_announcements.html")

@app.route("/events_calendar")
def events_calendar():
    return render_template("events_calendar.html")