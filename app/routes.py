from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from .models import Gym, User, Workout, Exercise, WorkoutExercise, Booking
from . import db
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@main.route('/booking', methods=['GET', 'POST'])
@login_required
def booking():
    if request.method == 'POST':
        gym_id = request.form.get('gym_id')
        date = request.form.get('date')
        time_slot = request.form.get('time_slot')
        
        # Create new booking
        booking = Booking(
            user_id=current_user.id,
            gym_id=gym_id,
            date=datetime.strptime(date, '%Y-%m-%d').date(),
            time_slot=time_slot
        )
        db.session.add(booking)
        db.session.commit()
        
        flash('Booking successful!', 'success')
        return redirect(url_for('main.booking'))
    
    # GET request - show the booking form and existing bookings
    gyms = Gym.query.filter_by(is_active=True).all()
    user_bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.date, Booking.time_slot).all()
    return render_template('booking.html', gyms=gyms, now=datetime.utcnow(), bookings=user_bookings)

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.profile'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if username or email already exists
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists. Please choose another one.', 'danger')
            return redirect(url_for('main.register'))
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already registered. Please use another email.', 'danger')
            return redirect(url_for('main.register'))

        # Create new user
        new_user = User(
            username=username,
            email=email
        )
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            return redirect(url_for('main.register'))

    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.profile'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        # Check if trying to login as admin
        if username == 'admin' and password == 'admin':
            # Create admin user if it doesn't exist
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@example.com',
                    is_admin=True,
                    is_active=True
                )
                admin.set_password('admin')
                db.session.add(admin)
                db.session.commit()
                user = admin
            else:
                user = admin
        
        if user and (user.check_password(password) or (username == 'admin' and password == 'admin')):
            login_user(user)
            return redirect(url_for('main.profile'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main.route('/workouts')
@login_required
def workouts():
    user_workouts = Workout.query.filter_by(user_id=current_user.id).order_by(Workout.date.desc()).all()
    return render_template('workouts.html', workouts=user_workouts)

@main.route('/workout/new', methods=['GET', 'POST'])
@login_required
def new_workout():
    if request.method == 'POST':
        try:
            # Create the workout
            workout = Workout(
                name=request.form.get('workout_name'),
                notes=request.form.get('notes'),
                user_id=current_user.id,
                date=datetime.utcnow()
            )
            db.session.add(workout)
            db.session.flush()  # Get the workout ID without committing

            # Add exercises
            exercise_ids = request.form.getlist('exercise_id')
            sets = request.form.getlist('sets')
            reps = request.form.getlist('reps')
            weights = request.form.getlist('weight')

            for i in range(len(exercise_ids)):
                if exercise_ids[i]:  # Only add if exercise is selected
                    workout_exercise = WorkoutExercise(
                        workout_id=workout.id,
                        exercise_id=exercise_ids[i],
                        sets=int(sets[i]) if sets[i] else None,
                        reps=int(reps[i]) if reps[i] else None,
                        weight=float(weights[i]) if weights[i] else None
                    )
                    db.session.add(workout_exercise)

            db.session.commit()
            flash('Workout created successfully!', 'success')
            return redirect(url_for('main.workouts'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating the workout. Please try again.', 'danger')
            return redirect(url_for('main.new_workout'))
    
    # GET request - show the form
    exercises = Exercise.query.filter_by(is_active=True).order_by(Exercise.name).all()
    return render_template('new_workout.html', exercises=exercises)

@main.route('/workout/<int:workout_id>')
@login_required
def view_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    if workout.user_id != current_user.id:
        flash('You do not have permission to view this workout.', 'danger')
        return redirect(url_for('main.workouts'))
    return render_template('view_workout.html', workout=workout)

@main.route('/workout/<int:workout_id>/delete', methods=['POST'])
@login_required
def delete_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    if workout.user_id != current_user.id:
        flash('You do not have permission to delete this workout.', 'danger')
        return redirect(url_for('main.workouts'))
    
    try:
        # Delete associated workout exercises first
        WorkoutExercise.query.filter_by(workout_id=workout_id).delete()
        db.session.delete(workout)
        db.session.commit()
        flash('Workout deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the workout.', 'danger')
    
    return redirect(url_for('main.workouts'))

@main.route('/exercises')
@login_required
def exercises():
    exercises = Exercise.query.filter_by(is_active=True).order_by(Exercise.name).all()
    return render_template('exercises.html', exercises=exercises)

@main.route('/gyms')
def gyms():
    gyms = Gym.query.filter_by(is_active=True).all()
    return render_template('gyms.html', gyms=gyms)

@main.route('/debug/exercises')
def debug_exercises():
    exercises = Exercise.query.all()
    return jsonify([{
        'id': e.id,
        'name': e.name,
        'muscle_group': e.muscle_group,
        'is_active': e.is_active
    } for e in exercises])
