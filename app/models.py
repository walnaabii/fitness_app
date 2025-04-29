from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login_manager
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Gym(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150))
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    workouts = db.relationship('Workout', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    muscle_group = db.Column(db.String(100))
    equipment = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    workout_exercises = db.relationship('WorkoutExercise', backref='exercise', lazy=True)

    # Pre-set exercises
    PRESET_EXERCISES = [
        {
            'name': 'Bench Press',
            'description': 'Lie on a bench and press a barbell or dumbbells upward from chest level.',
            'muscle_group': 'Chest',
            'equipment': 'Barbell, Bench'
        },
        {
            'name': 'Squats',
            'description': 'Stand with feet shoulder-width apart and lower body by bending knees and hips.',
            'muscle_group': 'Legs',
            'equipment': 'Barbell, Squat Rack'
        },
        {
            'name': 'Deadlift',
            'description': 'Lift a barbell from the ground to hip level while keeping back straight.',
            'muscle_group': 'Back',
            'equipment': 'Barbell'
        },
        {
            'name': 'Pull-ups',
            'description': 'Hang from a bar and pull body up until chin is above the bar.',
            'muscle_group': 'Back',
            'equipment': 'Pull-up Bar'
        },
        {
            'name': 'Push-ups',
            'description': 'Lower and raise body using arms while keeping body straight.',
            'muscle_group': 'Chest',
            'equipment': 'None'
        },
        {
            'name': 'Shoulder Press',
            'description': 'Press weights overhead while standing or sitting.',
            'muscle_group': 'Shoulders',
            'equipment': 'Dumbbells, Barbell'
        },
        {
            'name': 'Bicep Curls',
            'description': 'Curl weights upward while keeping elbows close to body.',
            'muscle_group': 'Arms',
            'equipment': 'Dumbbells, Barbell'
        },
        {
            'name': 'Tricep Dips',
            'description': 'Lower and raise body using parallel bars, focusing on triceps.',
            'muscle_group': 'Arms',
            'equipment': 'Parallel Bars'
        },
        {
            'name': 'Plank',
            'description': 'Hold a push-up position with forearms on the ground.',
            'muscle_group': 'Core',
            'equipment': 'None'
        },
        {
            'name': 'Lunges',
            'description': 'Step forward and lower body until front knee is at 90 degrees.',
            'muscle_group': 'Legs',
            'equipment': 'None'
        }
    ]

    @classmethod
    def initialize_preset_exercises(cls):
        """Initialize the database with preset exercises if they don't exist."""
        for exercise_data in cls.PRESET_EXERCISES:
            if not cls.query.filter_by(name=exercise_data['name']).first():
                exercise = cls(**exercise_data, is_active=True)
                db.session.add(exercise)
        db.session.commit()

class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exercises = db.relationship('WorkoutExercise', backref='workout', lazy=True)

class WorkoutExercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    sets = db.Column(db.Integer)
    reps = db.Column(db.Integer)
    weight = db.Column(db.Float)
    notes = db.Column(db.Text)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    gym_id = db.Column(db.Integer, db.ForeignKey('gym.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time_slot = db.Column(db.String(10), nullable=False)  # Format: "HH:MM"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='user_bookings')
    gym = db.relationship('Gym', backref='gym_bookings')
