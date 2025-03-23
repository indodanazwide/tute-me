import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Module, TutorModule, TutorAvailability, Booking
from datetime import time, date

# Create the Flask app and database context
app = create_app()
app.app_context().push()

# Clear existing data
db.drop_all()
db.create_all()

admin = [
    User(
        username="admin",
        email="admin@example.com",
        name="John",
        surname="Doe",
        role="admin",
    )
]

# Seed Users (Students and Tutors)
students = [
    User(
        username="student1",
        email="student1@example.com",
        name="John",
        surname="Doe",
        role="student"
    ),
    User(
        username="student2",
        email="student2@example.com",
        name="Jane",
        surname="Smith",
        role="student"
    )
]

tutors = [
    User(
        username="tutor1",
        email="tutor1@example.com",
        name="Alice",
        surname="Johnson",
        role="tutor"
    ),
    User(
        username="tutor2",
        email="tutor2@example.com",
        name="Bob",
        surname="Brown",
        role="tutor"
    )
]

# Set passwords for all users
for user in students + tutors + admin:
    user.set_password("password123")  # Set a default password for all users

# Add users to the session
db.session.add_all(students + tutors + admin)
db.session.commit()

# Seed Modules
modules = [
    Module(
        module_name="Mathematics 101",
        module_code="MATH101",
        description="Introduction to basic mathematics."
    ),
    Module(
        module_name="Physics 201",
        module_code="PHYS201",
        description="Advanced topics in physics."
    )
]

# Add modules to the session
db.session.add_all(modules)
db.session.commit()

# Seed Tutor-Module Associations
tutor_modules = [
    TutorModule(tutor_id=tutors[0].user_id, module_id=modules[0].module_id),
    TutorModule(tutor_id=tutors[0].user_id, module_id=modules[1].module_id),
    TutorModule(tutor_id=tutors[1].user_id, module_id=modules[0].module_id)
]

# Add tutor-module associations to the session
db.session.add_all(tutor_modules)
db.session.commit()

# Seed Tutor Availability
tutor_availability = [
    TutorAvailability(
        tutor_id=tutors[0].user_id,
        module_id=modules[0].module_id,
        day_of_week="Monday",
        start_time=time(10, 0),  # 10:00 AM
        end_time=time(11, 0)     # 11:00 AM
    ),
    TutorAvailability(
        tutor_id=tutors[0].user_id,
        module_id=modules[1].module_id,
        day_of_week="Tuesday",
        start_time=time(14, 0),  # 2:00 PM
        end_time=time(15, 0)     # 3:00 PM
    ),
    TutorAvailability(
        tutor_id=tutors[1].user_id,
        module_id=modules[0].module_id,
        day_of_week="Wednesday",
        start_time=time(9, 0),   # 9:00 AM
        end_time=time(10, 0)     # 10:00 AM
    )
]

# Add tutor availability to the session
db.session.add_all(tutor_availability)
db.session.commit()

# Seed Bookings
bookings = [
    Booking(
        student_id=students[0].user_id,
        tutor_id=tutors[0].user_id,
        module_id=modules[0].module_id,
        availability_id=tutor_availability[0].availability_id,
        booking_date=date(2023, 10, 16)  # Example date
    ),
    Booking(
        student_id=students[1].user_id,
        tutor_id=tutors[1].user_id,
        module_id=modules[0].module_id,
        availability_id=tutor_availability[2].availability_id,
        booking_date=date(2023, 10, 18)  # Example date
    )
]

# Add bookings to the session
db.session.add_all(bookings)
db.session.commit()

print("Database seeded successfully!")