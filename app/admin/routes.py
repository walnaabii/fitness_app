from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from ..models import User, Gym, Exercise, Workout, db
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
        is_active = request.form.get('is_active') == 'on'

        new_gym = Gym(
            name=name,
            location=location,
            is_active=is_active
        )
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
    recent_workouts_count = Workout.query.filter(Workout.date >= datetime.utcnow() - timedelta(days=7)).count()
    recent_workouts = Workout.query.order_by(Workout.date.desc()).limit(5).all()

    # Exercise statistics
    total_exercises = Exercise.query.count()
    active_exercises = Exercise.query.filter_by(is_active=True).count()

    # Recent users
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         new_users=new_users,
                         active_users=active_users,
                         total_gyms=total_gyms,
                         active_gyms=active_gyms,
                         total_workouts=total_workouts,
                         recent_workouts_count=recent_workouts_count,
                         recent_workouts=recent_workouts,
                         total_exercises=total_exercises,
                         active_exercises=active_exercises,
                         recent_users=recent_users)

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