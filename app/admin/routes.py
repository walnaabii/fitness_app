from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from ..models import User, Gym, Exercise, Workout, Analytics, db
from datetime import datetime, timedelta
from sqlalchemy import func

admin = Blueprint('admin', __name__)

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # User statistics
    total_users = User.query.count()
    new_users = User.query.filter(User.created_at >= datetime.utcnow() - timedelta(days=7)).count()
    active_users = User.query.filter_by(is_active=True).count()

    # Gym statistics
    total_gyms = Gym.query.count()
    active_gyms = Gym.query.filter_by(is_active=True).count()

    # Workout statistics
    total_workouts = Workout.query.count()
    recent_workouts = Workout.query.filter(Workout.date >= datetime.utcnow() - timedelta(days=7)).count()

    # Exercise statistics
    total_exercises = Exercise.query.count()
    active_exercises = Exercise.query.filter_by(is_active=True).count()

    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         new_users=new_users,
                         active_users=active_users,
                         total_gyms=total_gyms,
                         active_gyms=active_gyms,
                         total_workouts=total_workouts,
                         recent_workouts=recent_workouts,
                         total_exercises=total_exercises,
                         active_exercises=active_exercises)

@admin.route('/users')
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin.route('/user/<int:user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    flash(f'User {user.username} has been {"activated" if user.is_active else "deactivated"}.', 'success')
    return redirect(url_for('admin.users'))

@admin.route('/gyms')
@login_required
@admin_required
def gyms():
    gyms = Gym.query.all()
    return render_template('admin/gyms.html', gyms=gyms)

@admin.route('/gym/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_gym():
    if request.method == 'POST':
        name = request.form.get('name')
        location = request.form.get('location')
        description = request.form.get('description')

        new_gym = Gym(name=name, location=location, description=description)
        db.session.add(new_gym)
        db.session.commit()
        flash('Gym added successfully!', 'success')
        return redirect(url_for('admin.gyms'))

    return render_template('admin/new_gym.html')

@admin.route('/gym/<int:gym_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_gym(gym_id):
    gym = Gym.query.get_or_404(gym_id)
    gym.is_active = not gym.is_active
    db.session.commit()
    flash(f'Gym {gym.name} has been {"activated" if gym.is_active else "deactivated"}.', 'success')
    return redirect(url_for('admin.gyms'))

@admin.route('/exercises')
@login_required
@admin_required
def exercises():
    exercises = Exercise.query.all()
    return render_template('admin/exercises.html', exercises=exercises)

@admin.route('/exercise/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_exercise():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        muscle_group = request.form.get('muscle_group')
        equipment = request.form.get('equipment')

        new_exercise = Exercise(
            name=name,
            description=description,
            muscle_group=muscle_group,
            equipment=equipment
        )
        db.session.add(new_exercise)
        db.session.commit()
        flash('Exercise added successfully!', 'success')
        return redirect(url_for('admin.exercises'))

    return render_template('admin/new_exercise.html')

@admin.route('/exercise/<int:exercise_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_exercise(exercise_id):
    exercise = Exercise.query.get_or_404(exercise_id)
    exercise.is_active = not exercise.is_active
    db.session.commit()
    flash(f'Exercise {exercise.name} has been {"activated" if exercise.is_active else "deactivated"}.', 'success')
    return redirect(url_for('admin.exercises'))

@admin.route('/analytics')
@login_required
@admin_required
def analytics():
    # User growth
    user_growth = db.session.query(
        func.date(User.created_at).label('date'),
        func.count(User.id).label('count')
    ).group_by(func.date(User.created_at)).all()

    # Workout trends
    workout_trends = db.session.query(
        func.date(Workout.date).label('date'),
        func.count(Workout.id).label('count')
    ).group_by(func.date(Workout.date)).all()

    # Popular exercises
    popular_exercises = db.session.query(
        Exercise.name,
        func.count(WorkoutExercise.id).label('count')
    ).join(WorkoutExercise).group_by(Exercise.id).order_by(func.count(WorkoutExercise.id).desc()).limit(10).all()

    return render_template('admin/analytics.html',
                         user_growth=user_growth,
                         workout_trends=workout_trends,
                         popular_exercises=popular_exercises) 