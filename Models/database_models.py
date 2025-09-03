# models/database_models.py - SQLAlchemy Database Models
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dataclasses import dataclass

db = SQLAlchemy()


class Referee(db.Model):
    __tablename__ = 'referees'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    category = db.Column(db.Integer, nullable=False)  # 1 or 2
    role = db.Column(db.String(20), nullable=False)  # 'Referee' or 'Assistant Referee'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    assignments = db.relationship('RefereeAssignment', backref='referee', lazy=True, cascade='all, delete-orphan')

    def __init__(self, first_name, last_name, email, category, role):
        self.first_name = first_name.strip()
        self.last_name = last_name.strip()
        self.email = email.strip().lower()
        self.category = category
        self.role = role

        # Validation
        if self.category not in [1, 2]:
            raise ValueError("Category must be 1 or 2")
        if self.role not in ['Referee', 'Assistant Referee']:
            raise ValueError("Role must be 'Referee' or 'Assistant Referee'")

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'category': self.category,
            'role': self.role
        }


class League(db.Model):
    __tablename__ = 'leagues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    team_count = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    teams = db.relationship('Team', backref='league', lazy=True, cascade='all, delete-orphan')
    matches = db.relationship('Match', backref='league', lazy=True, cascade='all, delete-orphan')

    def __init__(self, name, team_count):
        self.name = name.strip()
        self.team_count = team_count

        # Validation
        if not (4 <= self.team_count <= 6):
            raise ValueError("Team count must be between 4 and 6")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'team_count': self.team_count
        }


class Team(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    home_matches = db.relationship('Match', foreign_keys='Match.team1_id', backref='team1', lazy=True)
    away_matches = db.relationship('Match', foreign_keys='Match.team2_id', backref='team2', lazy=True)

    # Unique constraint for team name within league
    __table_args__ = (db.UniqueConstraint('name', 'league_id', name='unique_team_per_league'),)

    def __init__(self, name, league_id):
        self.name = name.strip()
        self.league_id = league_id

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'league_id': self.league_id
        }


class Match(db.Model):
    __tablename__ = 'matches'

    id = db.Column(db.Integer, primary_key=True)
    team1_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    team2_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    assignments = db.relationship('RefereeAssignment', backref='match', lazy=True, cascade='all, delete-orphan')

    def __init__(self, team1_id, team2_id, date, league_id):
        self.team1_id = team1_id
        self.team2_id = team2_id
        self.date = datetime.fromisoformat(date).date() if isinstance(date, str) else date
        self.league_id = league_id

        # Validation
        if self.team1_id == self.team2_id:
            raise ValueError("Team cannot play against itself")

    def to_dict(self):
        return {
            'id': self.id,
            'team1_id': self.team1_id,
            'team2_id': self.team2_id,
            'date': self.date.isoformat(),
            'league_id': self.league_id
        }


class RefereeAssignment(db.Model):
    __tablename__ = 'referee_assignments'

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)
    referee_id = db.Column(db.Integer, db.ForeignKey('referees.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'Referee' or 'Assistant Referee'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Unique constraint to prevent duplicate assignments
    __table_args__ = (
        db.UniqueConstraint('match_id', 'referee_id', name='unique_referee_per_match'),
    )

    def __init__(self, match_id, referee_id, role):
        self.match_id = match_id
        self.referee_id = referee_id
        self.role = role

    def to_dict(self):
        return {
            'id': self.id,
            'match_id': self.match_id,
            'referee_id': self.referee_id,
            'role': self.role
        }


# Database initialization function
def init_db(app):
    """Initialize the database with the Flask app"""
    db.init_app(app)

    with app.app_context():
        # Create all tables
        db.create_all()

        # Initialize with sample data if tables are empty
        if Referee.query.count() == 0:
            init_sample_data()


def init_sample_data():
    """Initialize database with sample data"""
    try:
        # Sample referees
        sample_referees = [
            Referee('John', 'Smith', 'john.smith@email.com', 1, 'Referee'),
            Referee('Maria', 'Garcia', 'maria.garcia@email.com', 1, 'Assistant Referee'),
            Referee('David', 'Wilson', 'david.wilson@email.com', 2, 'Assistant Referee'),
            Referee('Sarah', 'Johnson', 'sarah.johnson@email.com', 1, 'Referee'),
            Referee('Michael', 'Brown', 'michael.brown@email.com', 2, 'Assistant Referee'),
        ]

        for referee in sample_referees:
            db.session.add(referee)

        # Sample league
        league = League('Premier Division', 4)
        db.session.add(league)
        db.session.flush()  # Get the league ID

        # Sample teams
        team_names = ['Arsenal FC', 'Chelsea FC', 'Liverpool FC', 'Manchester United']
        teams = []
        for name in team_names:
            team = Team(name, league.id)
            teams.append(team)
            db.session.add(team)

        db.session.flush()  # Get team IDs

        # Sample match
        from datetime import date, timedelta
        match_date = date.today() + timedelta(days=7)
        match = Match(teams[0].id, teams[1].id, match_date, league.id)
        db.session.add(match)

        db.session.commit()
        print("Sample data initialized successfully!")

    except Exception as e:
        db.session.rollback()
        print(f"Error initializing sample data: {e}")