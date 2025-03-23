import datetime
from flask import flash, redirect, render_template, request, session, url_for
from app.models import Booking, Module, TutorAvailability, TutorModule, User, db
from . import router

@router.route('/admin_dashboard')
def admin_dashboard():
    # Ensure the user is logged in as an admin
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Please log in as an admin", "error")
        return redirect(url_for('main.login'))
    
    # Fetch all tutors
    tutors = User.query.filter_by(role='tutor').all()
    return render_template('admin_dashboard.html', tutors=tutors)

@router.route('/view_all_users', methods=['GET'])
def view_all_users():
    # Ensure the user is logged in as an admin
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Please log in as an admin', 'error')
        return redirect(url_for('main.login'))

    try:
        # Get search query from request
        search_query = request.args.get('search', '')

        # Pagination settings
        page = request.args.get('page', 1, type=int)
        per_page = 10  # Number of users per page

        # Query users with optional search filter
        query = User.query
        if search_query:
            query = query.filter(
                (User.name.ilike(f'%{search_query}%')) |
                (User.username.ilike(f'%{search_query}%')) |
                (User.email.ilike(f'%{search_query}%'))
            )
        users = query.order_by(User.name.asc()).paginate(page=page, per_page=per_page)

        return render_template('view_all_users.html', users=users.items, pagination=users)
    except Exception as e:
        # Log the error and display a user-friendly message
        print(f"Error fetching users: {e}")
        flash('An error occurred while fetching users. Please try again.', 'error')
        return redirect(url_for('main.admin_dashboard'))

@router.route('/view_tutor/<int:tutor_id>', methods=['GET'])
def view_tutor(tutor_id):
    # Ensure the user is logged in as an admin
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Please log in as an admin', 'error')
        return redirect(url_for('main.login'))

    try:
        # Fetch the tutor
        tutor = User.query.get_or_404(tutor_id)

        # Fetch the tutor's assigned modules
        tutor_modules = TutorModule.query.filter_by(tutor_id=tutor_id).all()
        modules = [Module.query.get(tm.module_id) for tm in tutor_modules]

        # Fetch the tutor's availability slots with module details
        availability = (
            db.session.query(TutorAvailability, Module)
            .join(Module, TutorAvailability.module_id == Module.module_id)
            .filter(TutorAvailability.tutor_id == tutor_id)
            .all()
        )

        return render_template(
            'view_tutor.html',
            tutor=tutor,
            modules=modules,
            availability=availability
        )
    except Exception as e:
        # Log the error and display a user-friendly message
        print(f"Error fetching tutor details: {e}")
        flash('An error occurred while fetching tutor details. Please try again.', 'error')
        return redirect(url_for('main.admin_dashboard'))
    
@router.route('/edit_tutor/<int:tutor_id>', methods=['GET', 'POST'])
def edit_tutor(tutor_id):
    # Ensure the user is logged in as an admin
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Please log in as an admin', 'error')
        return redirect(url_for('main.login'))

    tutor = User.query.get_or_404(tutor_id)
    modules = Module.query.all()
    availability = TutorAvailability.query.filter_by(tutor_id=tutor_id).all()

    if request.method == 'POST':
        try:
            # Update tutor details
            tutor.name = request.form.get('name', tutor.name)
            tutor.surname = request.form.get('surname', tutor.surname)
            tutor.username = request.form.get('username', tutor.username)

            # Update module assignments
            module_ids = request.form.getlist('module_ids')
            TutorModule.query.filter_by(tutor_id=tutor_id).delete()  # Remove existing assignments
            for module_id in module_ids:
                new_assignment = TutorModule(tutor_id=tutor_id, module_id=module_id)
                db.session.add(new_assignment)

            # Update availability
            availability_ids = request.form.getlist('availability_ids')
            TutorAvailability.query.filter_by(tutor_id=tutor_id).delete()  # Remove existing availability
            for availability_id in availability_ids:
                day_of_week = request.form.get(f'day_of_week_{availability_id}')
                start_time = datetime.strptime(request.form.get(f'start_time_{availability_id}'), '%H:%M').time()
                end_time = datetime.strptime(request.form.get(f'end_time_{availability_id}'), '%H:%M').time()
                module_id = request.form.get(f'module_id_{availability_id}')
                new_availability = TutorAvailability(
                    tutor_id=tutor_id,
                    module_id=module_id,
                    day_of_week=day_of_week,
                    start_time=start_time,
                    end_time=end_time
                )
                db.session.add(new_availability)

            db.session.commit()
            flash('Tutor details updated successfully!', 'success')
            return redirect(url_for('main.view_tutor', tutor_id=tutor_id))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the tutor. Please try again.', 'error')
            print(f"Error: {e}")

    return render_template('edit_tutor.html', tutor=tutor, modules=modules, availability=availability)

@router.route('/remove_tutor/<int:tutor_id>', methods=['GET', 'POST'])
def remove_tutor(tutor_id):
    # Ensure the user is logged in as an admin
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Please log in as an admin', 'error')
        return redirect(url_for('main.login'))

    tutor = User.query.get_or_404(tutor_id)

    if request.method == 'POST':
        try:
            # Delete related records
            Booking.query.filter_by(tutor_id=tutor_id).delete()
            TutorAvailability.query.filter_by(tutor_id=tutor_id).delete()
            TutorModule.query.filter_by(tutor_id=tutor_id).delete()
            User.query.filter_by(user_id=tutor_id).delete()

            db.session.commit()
            flash('Tutor removed successfully!', 'success')
            return redirect(url_for('main.admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while removing the tutor. Please try again.', 'error')
            print(f"Error: {e}")

    return render_template('remove_tutor.html', tutor=tutor)

@router.route('/add_tutor', methods=['GET', 'POST'])
def add_tutor():
    # Ensure the user is logged in as an admin
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Please log in as an admin', 'error')
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        try:
            # Create new tutor
            username = request.form.get('username')
            password = request.form.get('password')
            name = request.form.get('name')
            surname = request.form.get('surname')
            email = request.form.get('email')

            # Check if username already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Username already exists. Please choose a different one.', 'error')
                return redirect(url_for('main.add_tutor'))

            new_tutor = User(
                username=username,
                role='tutor',
                name=name,
                surname=surname,
                 email=email
            )
            new_tutor.set_password(password)

            db.session.add(new_tutor)
            db.session.commit()

            # Assign modules
            module_ids = request.form.getlist('module_ids')
            for module_id in module_ids:
                new_assignment = TutorModule(tutor_id=new_tutor.user_id, module_id=module_id)
                db.session.add(new_assignment)

            # Add availability
            availability_count = int(request.form.get('availability_count', 0))
            for i in range(availability_count):
                day_of_week = request.form.get(f'day_of_week_{i}')
                start_time = datetime.strptime(request.form.get(f'start_time_{i}'), '%H:%M').time()
                end_time = datetime.strptime(request.form.get(f'end_time_{i}'), '%H:%M').time()
                module_id = request.form.get(f'module_id_{i}')
                new_availability = TutorAvailability(
                    tutor_id=new_tutor.user_id,
                    module_id=module_id,
                    day_of_week=day_of_week,
                    start_time=start_time,
                    end_time=end_time
                )
                db.session.add(new_availability)

            db.session.commit()
            flash('Tutor added successfully!', 'success')
            return redirect(url_for('main.admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the tutor. Please try again.', 'error')
            print(f"Error: {e}")

    modules = Module.query.all()
    return render_template('add_tutor.html', modules=modules)