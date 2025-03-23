import datetime
from flask import flash, redirect, render_template, request, session, url_for
from app.models import Booking, Module, TutorAvailability, TutorModule, User
from . import router

@router.route('/tutor_dashboard')
def tutor_dashboard():
    # Ensure the user is logged in as a tutor
    if 'user_id' not in session or session.get('role') != 'tutor':
        flash("Please log in as a tutor", "error")
        return redirect(url_for('main.login'))
    
    tutor_id = session.get('user_id')
    
    # Fetch the tutor's modules
    tutor_modules = TutorModule.query.filter_by(tutor_id=tutor_id).all()
    modules = [Module.query.get(tm.module_id) for tm in tutor_modules]
    
    # Fetch the tutor's availability slots with module names
    availability = (
        TutorAvailability.query
        .filter_by(tutor_id=tutor_id)
        .join(Module, TutorAvailability.module_id == Module.module_id)
        .add_columns(
            TutorAvailability.availability_id,
            TutorAvailability.day_of_week,
            TutorAvailability.start_time,
            TutorAvailability.end_time,
            Module.module_name
        )
        .all()
    )

    return render_template('tutor_dashboard.html', modules=modules, availability=availability)

@router.route('/view_tutor_bookings')
def view_tutor_bookings():
    # Ensure the user is logged in as a tutor
    if 'user_id' not in session or session.get('role') != 'tutor':
        flash("Please log in as a tutor", "error")
        return redirect(url_for('main.login'))

    tutor_id = session.get('user_id')
    
    # Fetch all bookings for the tutor
    bookings = (
        Booking.query
        .filter_by(tutor_id=tutor_id)
        .join(User, Booking.student_id == User.user_id)
        .join(Module, Booking.module_id == Module.module_id)
        .join(TutorAvailability, Booking.availability_id == TutorAvailability.availability_id)
        .add_columns(
            Booking.booking_id,
            Booking.booking_date,
            User.name.label('student_name'),
            User.surname.label('student_surname'),
            Module.module_name,
            TutorAvailability.day_of_week,
            TutorAvailability.start_time,
            TutorAvailability.end_time
        )
        .all()
    )

    return render_template('view_tutor_bookings.html', bookings=bookings)

