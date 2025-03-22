from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    role = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(80), nullable=False)   
    surname = db.Column(db.String(80), nullable=False)

class Module(db.Model):
    __tablename__ = 'modules'
    module_id = db.Column(db.Integer, primary_key=True)
    module_name = db.Column(db.String(80), nullable=False)
    module_code = db.Column(db.String(10), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=True)

class TutorModule(db.Model):
    __tablename__ = 'tutor_modules'
    tutor_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.module_id'), primary_key=True)

class TutorAvailability(db.Model):
    __tablename__ = 'tutor_availability'
    availability_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.module_id'), nullable=False)
    day_of_week = db.Column(db.String(10), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    module = db.relationship('Module', backref='tutor_availabilities') 

    __table_args__ = (
        db.UniqueConstraint('tutor_id', 'module_id', 'day_of_week', 'start_time', 'end_time', name='unique_availability'),
    )

class Booking(db.Model):
    __tablename__ = 'bookings'
    booking_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    tutor_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.module_id'), nullable=False)
    availability_id = db.Column(db.Integer, db.ForeignKey('tutor_availability.availability_id'), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)

    module = db.relationship('Module', backref='bookings')
    tutor = db.relationship('User', foreign_keys=[tutor_id], backref='tutor_bookings')
    student = db.relationship('User', foreign_keys=[student_id], backref='student_bookings') 
    availability = db.relationship('TutorAvailability', backref='bookings')

    __table_args__ = (
        db.UniqueConstraint('tutor_id', 'module_id', 'booking_date', 'availability_id', name='unique_booking'),
    )