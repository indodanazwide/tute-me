import datetime
from flask import flash, redirect, render_template, request, session, url_for

from app.models import Booking, Module, TutorAvailability, TutorModule, User, db
from . import router

@router.route('/student_dashboard')
def student_dashboard():
    # Ensure the user is logged in and is a student
    if 'user_id' not in session or session.get('role') != 'student':
        flash('You must be logged in as a student to access this page.', 'error')
        return redirect(url_for('main.login'))

    user_id = session['user_id']

    # Fetch the student's booked sessions
    booked_sessions = (
        Booking.query
        .filter_by(student_id=user_id)
        .join(Module, Booking.module_id == Module.module_id)
        .join(User, Booking.tutor_id == User.user_id)
        .join(TutorAvailability, Booking.availability_id == TutorAvailability.availability_id)
        .add_columns(
            Module.module_name,
            User.name.label('tutor_name'),
            User.surname.label('tutor_surname'),
            Booking.booking_date,
            TutorAvailability.day_of_week,
            TutorAvailability.start_time,
            TutorAvailability.end_time
        )
        .all()
    )

    # Fetch available modules (optional)
    available_modules = Module.query.all()

    return render_template('student_dashboard.html', booked_sessions=booked_sessions, available_modules=available_modules)

@router.route('/search_modules', methods=['GET', 'POST'])
def search_modules():
    # Ensure the user is logged in as a student
    if 'user_id' not in session or session.get('role') != 'student':
        flash("Please log in as a student", "error")
        return redirect(url_for('main.login'))
    
    modules = []
    search_term = ""
    if request.method == "POST":
        search_term = request.form.get("search_term", "").strip()
        if search_term:
            if len(search_term) > 100:  # Prevent excessively long search terms
                flash("Search term is too long.", "error")
            else:
                modules = Module.query.filter(
                    (Module.module_name.ilike(f"%{search_term}%")) | 
                    (Module.module_code.ilike(f"%{search_term}%"))
                ).all()
        else:
            # If no search term is provided, fetch all modules
            modules = Module.query.all()
    else:
        # On initial load, fetch all modules
        modules = Module.query.all()

    module_tutors = {}
    for module in modules:
        tutors = User.query.join(TutorModule).filter(
            TutorModule.module_id == module.module_id,
            User.role == 'tutor'
        ).all()
        module_tutors[module.module_id] = tutors
    
    return render_template('search_modules.html', modules=modules, module_tutors=module_tutors, search_term=search_term)

@router.route('/view_bookings')
def view_bookings():
    # Ensure the user is logged in as a student
    if 'user_id' not in session or session['role'] != 'student':
        flash('Please log in as a student', 'error')
        return redirect(url_for('main.login'))

    student_id = session['user_id']
    bookings = (
        Booking.query
        .filter_by(student_id=student_id)
        .join(Module, Booking.module_id == Module.module_id)
        .join(User, Booking.tutor_id == User.user_id)
        .join(TutorAvailability, Booking.availability_id == TutorAvailability.availability_id)
        .all()
    )
    return render_template('view_bookings.html', bookings=bookings)

@router.route('/book_session/<int:module_id>', methods=['GET', 'POST'])
def book_session(module_id):
    # Ensure the user is logged in as a student
    if 'user_id' not in session or session['role'] != 'student':
        flash('Please log in as a student', 'error')
        return redirect(url_for('main.login'))

    module = Module.query.get_or_404(module_id)
    tutor_modules = TutorModule.query.filter_by(module_id=module_id).all()
    tutor_ids = [tm.tutor_id for tm in tutor_modules]
    tutors = User.query.filter(User.user_id.in_(tutor_ids), User.role == 'tutor').all()

    if request.method == 'POST':
        try:
            tutor_id = int(request.form['tutor_id'])
            availability_id = int(request.form['availability_id'])
            booking_date_str = request.form['booking_date']

            booking_date = datetime.strptime(booking_date_str, '%Y-%m-%d').date()
        except (ValueError, KeyError):
            flash('Invalid input. Please check your selections.', 'error')
            return redirect(url_for('main.book_session', module_id=module_id))

        availability = TutorAvailability.query.filter_by(
            availability_id=availability_id,
            tutor_id=tutor_id,
            module_id=module_id
        ).first()

        if not availability:
            flash('Invalid availability slot.', 'error')
            return redirect(url_for('main.book_session', module_id=module_id))

        days_of_week = {
            'Monday': 0,
            'Tuesday': 1,
            'Wednesday': 2,
            'Thursday': 3,
            'Friday': 4,
            'Saturday': 5,
            'Sunday': 6
        }

        booking_weekday = booking_date.weekday()

        if booking_weekday != days_of_week.get(availability.day_of_week):
            flash(f'Invalid date. Please select a date that falls on {availability.day_of_week}.', 'error')
            return redirect(url_for('main.book_session', module_id=module_id))

        if booking_date < datetime.date.today():
            flash('Cannot book a session in the past.', 'error')
            return redirect(url_for('main.book_session', module_id=module_id))

        existing_booking = Booking.query.filter_by(
            tutor_id=tutor_id,
            module_id=module_id,
            availability_id=availability_id,
            booking_date=booking_date
        ).first()

        if existing_booking:
            flash('This slot is already booked.', 'error')
            return redirect(url_for('main.book_session', module_id=module_id))

        new_booking = Booking(
            student_id=session['user_id'],
            tutor_id=tutor_id,
            module_id=module_id,
            availability_id=availability_id,
            booking_date=booking_date
        )
        db.session.add(new_booking)
        db.session.commit()

        flash('Booking successful!', 'success')
        return redirect(url_for('main.student_dashboard'))

    selected_tutor_id = request.args.get('tutor_id', type=int)
    availability_slots = []
    if selected_tutor_id:
        availability_slots = TutorAvailability.query.filter_by(
            tutor_id=selected_tutor_id,
            module_id=module_id
        ).all()

    current_date = datetime.date.today().isoformat()

    return render_template('book_session.html', module=module, tutors=tutors, availability_slots=availability_slots, selected_tutor_id=selected_tutor_id, current_date=current_date)