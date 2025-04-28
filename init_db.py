from app import create_app, db
from app.models import User, Gym, Exercise, Workout, WorkoutExercise, Analytics

def init_db():
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create an admin user if none exists
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True,
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Created admin user")

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully!") 