from app import db
 
class Student(db.Model):
    __tablename__ = 'students'
    student_id = db.Column(db.Integer, primary_key=True,
                           unique=True, nullable=False)
    username = db.Column(db.String(20), nullable=False,
                         unique=True, index=True)
    firstname = db.Column(db.String(32))
    lastname = db.Column(db.String(32), nullable=False, index=True)
    email = db.Column(db.String(64), nullable=False, unique=True, index=True)
    active = db.Column(db.Boolean, default=True)
    loans = db.relationship('Loan', backref='student', lazy='select')

    def __repr__(self):
        return f"student('{self.username}', '{self.lastname}', '{self.firstname}', '{self.email}', '{self.active}', {self.loans})"

class Loan(db.Model):
    __tablename__ = 'loans'
    loan_id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.device_id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    borrowdatetime = db.Column(db.DateTime, nullable=False) 
    returndatetime = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"loan('{self.device_id}', '{self.borrowdatetime}', '{self.returndatetime}', '{self.student_id}')"
    
class Device(db.Model):
    __tablename__ = 'devices'
    device_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    device_type = db.Column(db.String(15), nullable=False)
    on_loan = db.Column(db.Boolean, default=False)
    loaned = db.relationship('Loan', backref='device', lazy='select')
    
    def __repr__(self):
        return f"device('{self.device_id}', '{self.device_type}', '{self.on_loan}', '{self.loaned}')"
