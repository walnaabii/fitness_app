from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from .models import Gym, User, Workout, Exercise, WorkoutExercise
from . import db
from datetime import datetime

main = Blueprint('main', __name__)

# Existing routes...
@main.route('/')
def home():
    return render_template('home.html')

@main.route('/gyms')
def gyms():
    all_gyms = Gym.query.all()
    return render_template('gym_list.html', gyms=all_gyms)

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@main.route('/booking')
def booking():
    return render_template('booking.html')

# 🔥 New Admin Route
@main.route('/admin/add-gym', methods=['GET', 'POST'])
def add_gym():
    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        description = request.form['description']

        new_gym = Gym(name=name, location=location, description=description)
        db.session.add(new_gym)
        db.session.commit()

        return redirect(url_for('main.gyms'))
    
    return render_template('add_gym.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.profile'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        age = request.form.get('age')
        weight = request.form.get('weight')
        height = request.form.get('height')
        fitness_goal = request.form.get('fitness_goal')

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
            email=email,
            age=age if age else None,
            weight=float(weight) if weight else None,
            height=float(height) if height else None,
            fitness_goal=fitness_goal
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
        
        if user and user.check_password(password):
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
        workout_name = request.form.get('workout_name')
        notes = request.form.get('notes')
        
        new_workout = Workout(
            name=workout_name,
            notes=notes,
            user_id=current_user.id
        )
        
        try:
            db.session.add(new_workout)
            db.session.commit()
            
            # Handle exercises
            exercise_ids = request.form.getlist('exercise_id')
            sets = request.form.getlist('sets')
            reps = request.form.getlist('reps')
            weights = request.form.getlist('weight')
            durations = request.form.getlist('duration')
            exercise_notes = request.form.getlist('exercise_notes')
            
            for i in range(len(exercise_ids)):
                workout_exercise = WorkoutExercise(
                    workout_id=new_workout.id,
                    exercise_id=exercise_ids[i],
                    sets=int(sets[i]) if sets[i] else None,
                    reps=int(reps[i]) if reps[i] else None,
                    weight=float(weights[i]) if weights[i] else None,
                    duration=int(durations[i]) if durations[i] else None,
                    notes=exercise_notes[i]
                )
                db.session.add(workout_exercise)
            
            db.session.commit()
            flash('Workout created successfully!', 'success')
            return redirect(url_for('main.workouts'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating the workout.', 'danger')
            return redirect(url_for('main.new_workout'))
    
    exercises = Exercise.query.all()
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
    exercises = Exercise.query.all()
    return render_template('exercises.html', exercises=exercises)
