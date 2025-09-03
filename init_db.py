# init_db.py - Database initialization script
"""
Run this script to initialize the database with sample data.
Usage: python init_db.py
"""

from app import app
from Models.database_models import db, init_sample_data, Referee, League, Team, Match, RefereeAssignment


def reset_database():
    """Reset the database by dropping and recreating all tables"""
    print("🗑️  Dropping all tables...")
    with app.app_context():
        db.drop_all()
        print("📊 Creating all tables...")
        db.create_all()
        print("🌱 Initializing with sample data...")
        init_sample_data()
        print("✅ Database initialization complete!")


def check_database_status():
    """Check the current status of the database"""
    with app.app_context():
        print("\n📊 Database Status:")
        print(f"Referees: {Referee.query.count()}")
        print(f"Leagues: {League.query.count()}")
        print(f"Teams: {Team.query.count()}")
        print(f"Matches: {Match.query.count()}")
        print(f"Assignments: {RefereeAssignment.query.count()}")

        if Referee.query.count() > 0:
            print("\n👥 Sample Referees:")
            for referee in Referee.query.limit(5):
                print(f"  - {referee.first_name} {referee.last_name} ({referee.role})")

        if League.query.count() > 0:
            print("\n🏆 Sample Leagues:")
            for league in League.query.all():
                teams_count = Team.query.filter_by(league_id=league.id).count()
                print(f"  - {league.name} ({teams_count} teams)")


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--reset':
        reset_database()
    else:
        # Just check status
        try:
            check_database_status()
        except Exception as e:
            print(f"❌ Database not initialized or error occurred: {e}")
            print("💡 Run 'python init_db.py --reset' to initialize the database")