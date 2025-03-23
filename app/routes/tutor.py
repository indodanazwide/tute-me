from flask import flash, redirect, render_template, session, url_for

from app.models import Module, TutorAvailability, TutorModule
from . import router

@router.route('/tutor_dashboard')
def tutor_dashboard():
    # Ensure the user is logged in as a tutor
    if 'user_id' not in session or session.get('role') != 'tutor':
        flash("Please log in as a tutor", "error")
        return redirect(url_for('main.login'))
    
    tutor_id = session.get('user_id')
    tutor_modules = TutorModule.query.filter_by(tutor_id=tutor_id).all()
    modules = [Module.query.get(tm.module_id) for tm in tutor_modules]
    
    # Fetch availability slots with module names
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
