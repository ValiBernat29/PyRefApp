# app.py - Updated Main Flask Application with SQLAlchemy
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime, date
import os
from Models.database_models import db, init_db, Referee, League, Team, Match, RefereeAssignment

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL') or f'sqlite:///{os.path.join(basedir, "referee_system.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
init_db(app)


@app.route('/')
def dashboard():
    """Dashboard with statistics and overview"""
    stats = {
        'referees': Referee.query.count(),
        'leagues': League.query.count(),
        'matches': Match.query.count(),
        'assignments': RefereeAssignment.query.count()
    }

    # Get upcoming matches
    today = date.today()
    upcoming_matches = db.session.query(Match).filter(Match.date >= today).order_by(Match.date).limit(5).all()

    upcoming_matches_data = []
    for match in upcoming_matches:
        assignments = RefereeAssignment.query.filter_by(match_id=match.id).all()
        assignment_details = []

        for assignment in assignments:
            referee = Referee.query.get(assignment.referee_id)
            assignment_details.append({
                'referee': referee,
                'role': assignment.role
            })

        upcoming_matches_data.append({
            'match': match,
            'team1': Team.query.get(match.team1_id),
            'team2': Team.query.get(match.team2_id),
            'league': League.query.get(match.league_id),
            'assignments': assignment_details
        })

    return render_template('dashboard.html', stats=stats, upcoming_matches=upcoming_matches_data)


# Referee Routes
@app.route('/referees')
def referees():
    """Referee management page"""
    all_referees = Referee.query.order_by(Referee.last_name, Referee.first_name).all()
    return render_template('referees.html', referees=all_referees)


@app.route('/api/referees', methods=['POST'])
def add_referee():
    """Add new referee via API"""
    data = request.get_json()
    try:
        # Check if email already exists
        existing_referee = Referee.query.filter_by(email=data['email'].strip().lower()).first()
        if existing_referee:
            return jsonify({'success': False, 'error': f"Referee with email {data['email']} already exists"}), 400

        referee = Referee(
            first_name=data['firstName'],
            last_name=data['lastName'],
            email=data['email'],
            category=int(data['category']),
            role=data['role']
        )

        db.session.add(referee)
        db.session.commit()

        return jsonify({'success': True, 'referee': referee.to_dict()})
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'An error occurred while creating the referee'}), 500


@app.route('/api/referees/<int:referee_id>', methods=['DELETE'])
def delete_referee(referee_id):
    """Delete referee via API"""
    try:
        referee = Referee.query.get_or_404(referee_id)

        # SQLAlchemy will handle cascade deletion of assignments
        db.session.delete(referee)
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'An error occurred while deleting the referee'}), 500


# League Routes
@app.route('/leagues')
def leagues():
    """League management page"""
    all_leagues = League.query.order_by(League.name).all()
    leagues_data = []

    for league in all_leagues:
        teams = Team.query.filter_by(league_id=league.id).order_by(Team.name).all()
        leagues_data.append({
            'league': league,
            'teams': teams
        })

    return render_template('leagues.html', leagues=leagues_data)


@app.route('/api/leagues', methods=['POST'])
def add_league():
    """Add new league with teams via API"""
    data = request.get_json()
    try:
        # Check if league name already exists
        existing_league = League.query.filter_by(name=data['name'].strip()).first()
        if existing_league:
            return jsonify({'success': False, 'error': f"League with name '{data['name']}' already exists"}), 400

        # Validate team count
        team_names = data['teams']
        if not (4 <= len(team_names) <= 6):
            return jsonify({'success': False, 'error': 'League must have between 4 and 6 teams'}), 400

        # Create league
        league = League(name=data['name'], team_count=len(team_names))
        db.session.add(league)
        db.session.flush()  # Get the league ID

        # Create teams
        for team_name in team_names:
            team = Team(name=team_name.strip(), league_id=league.id)
            db.session.add(team)

        db.session.commit()

        return jsonify({'success': True, 'league': league.to_dict()})
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'An error occurred while creating the league'}), 500


@app.route('/api/leagues/<int:league_id>/teams', methods=['POST'])
def add_team_to_league(league_id):
    """Add team to existing league via API"""
    data = request.get_json()
    try:
        league = League.query.get_or_404(league_id)

        # Check if league is full
        current_teams = Team.query.filter_by(league_id=league_id).count()
        if current_teams >= league.team_count:
            return jsonify(
                {'success': False, 'error': f'League already has maximum number of teams ({league.team_count})'}), 400

        # Check for duplicate team name in league
        existing_team = Team.query.filter_by(name=data['name'].strip(), league_id=league_id).first()
        if existing_team:
            return jsonify({'success': False, 'error': f"Team '{data['name']}' already exists in this league"}), 400

        team = Team(name=data['name'], league_id=league_id)
        db.session.add(team)
        db.session.commit()

        return jsonify({'success': True, 'team': team.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'An error occurred while adding the team'}), 500


# Match Routes
@app.route('/matches')
def matches():
    """Match management page"""
    all_matches = Match.query.order_by(Match.date.desc()).all()
    all_leagues = League.query.order_by(League.name).all()

    matches_data = []
    for match in all_matches:
        assignments = RefereeAssignment.query.filter_by(match_id=match.id).all()
        assignment_details = []

        for assignment in assignments:
            referee = Referee.query.get(assignment.referee_id)
            assignment_details.append({
                'referee': referee,
                'role': assignment.role
            })

        matches_data.append({
            'match': match,
            'team1': Team.query.get(match.team1_id),
            'team2': Team.query.get(match.team2_id),
            'league': League.query.get(match.league_id),
            'assignments': assignment_details
        })

    return render_template('matches.html', matches=matches_data, leagues=all_leagues)


@app.route('/api/matches', methods=['POST'])
def add_match():
    """Add new match via API"""
    data = request.get_json()
    try:
        # Validate teams exist and belong to same league
        team1 = Team.query.get(int(data['team1Id']))
        team2 = Team.query.get(int(data['team2Id']))
        league_id = int(data['leagueId'])

        if not team1 or not team2:
            return jsonify({'success': False, 'error': 'One or both teams not found'}), 400

        if team1.league_id != league_id or team2.league_id != league_id:
            return jsonify({'success': False, 'error': 'Teams must belong to the specified league'}), 400

        if team1.id == team2.id:
            return jsonify({'success': False, 'error': 'Team cannot play against itself'}), 400

        # Check for duplicate matches on same date
        match_date = datetime.fromisoformat(data['date']).date()
        existing_match = Match.query.filter(
            Match.date == match_date,
            ((Match.team1_id == team1.id) & (Match.team2_id == team2.id)) |
            ((Match.team1_id == team2.id) & (Match.team2_id == team1.id))
        ).first()

        if existing_match:
            return jsonify({'success': False, 'error': 'These teams are already scheduled to play on this date'}), 400

        match = Match(
            team1_id=team1.id,
            team2_id=team2.id,
            date=match_date,
            league_id=league_id
        )

        db.session.add(match)
        db.session.commit()

        return jsonify({'success': True, 'match': match.to_dict()})
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'An error occurred while creating the match'}), 500


@app.route('/api/leagues/<int:league_id>/teams')
def get_league_teams(league_id):
    """Get teams for a specific league"""
    teams = Team.query.filter_by(league_id=league_id).order_by(Team.name).all()
    return jsonify([team.to_dict() for team in teams])


# Assignment Routes
@app.route('/api/matches/<int:match_id>/assign', methods=['POST'])
def assign_referees_to_match(match_id):
    """Assign referees to a match"""
    data = request.get_json()
    try:
        match = Match.query.get_or_404(match_id)

        referee_id = int(data['refereeId'])
        assistant1_id = int(data['assistant1Id'])
        assistant2_id = int(data['assistant2Id'])

        # Validate referees exist and have correct roles
        referee = Referee.query.get(referee_id)
        assistant1 = Referee.query.get(assistant1_id)
        assistant2 = Referee.query.get(assistant2_id)

        if not referee or not assistant1 or not assistant2:
            return jsonify({'success': False, 'error': 'One or more referees not found'}), 400

        if referee.role != 'Referee':
            return jsonify({'success': False, 'error': 'Main referee must have "Referee" role'}), 400

        if assistant1.role != 'Assistant Referee' or assistant2.role != 'Assistant Referee':
            return jsonify({'success': False, 'error': 'Assistants must have "Assistant Referee" role'}), 400

        # Validate no duplicate referees
        referee_ids = {referee_id, assistant1_id, assistant2_id}
        if len(referee_ids) != 3:
            return jsonify({'success': False, 'error': 'Cannot assign the same referee to multiple positions'}), 400

        # Check for existing assignments for this match
        existing_assignments = RefereeAssignment.query.filter_by(match_id=match_id).first()
        if existing_assignments:
            return jsonify({'success': False, 'error': 'Match already has referee assignments'}), 400

        # Check referee availability on match date
        for ref_id in referee_ids:
            existing_assignment = db.session.query(RefereeAssignment).join(Match).filter(
                RefereeAssignment.referee_id == ref_id,
                Match.date == match.date
            ).first()

            if existing_assignment:
                ref = Referee.query.get(ref_id)
                return jsonify({
                    'success': False,
                    'error': f'Referee {ref.first_name} {ref.last_name} is already assigned to another match on {match.date}'
                }), 400

        # Create assignments
        assignments = [
            RefereeAssignment(match_id=match_id, referee_id=referee_id, role='Referee'),
            RefereeAssignment(match_id=match_id, referee_id=assistant1_id, role='Assistant Referee'),
            RefereeAssignment(match_id=match_id, referee_id=assistant2_id, role='Assistant Referee')
        ]

        for assignment in assignments:
            db.session.add(assignment)

        db.session.commit()

        return jsonify({'success': True, 'assignments': [a.to_dict() for a in assignments]})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'An error occurred while assigning referees'}), 500


@app.route('/api/matches/<int:match_id>/reassign', methods=['POST'])
def reassign_referees_to_match(match_id):
    """Reassign referees to a match (replaces existing assignments)"""
    data = request.get_json()
    try:
        match = Match.query.get_or_404(match_id)

        # Delete existing assignments for this match
        RefereeAssignment.query.filter_by(match_id=match_id).delete()

        # Now assign new referees (reuse the same logic)
        referee_id = int(data['refereeId'])
        assistant1_id = int(data['assistant1Id'])
        assistant2_id = int(data['assistant2Id'])

        # Validate referees exist and have correct roles
        referee = Referee.query.get(referee_id)
        assistant1 = Referee.query.get(assistant1_id)
        assistant2 = Referee.query.get(assistant2_id)

        if not referee or not assistant1 or not assistant2:
            return jsonify({'success': False, 'error': 'One or more referees not found'}), 400

        if referee.role != 'Referee':
            return jsonify({'success': False, 'error': 'Main referee must have "Referee" role'}), 400

        if assistant1.role != 'Assistant Referee' or assistant2.role != 'Assistant Referee':
            return jsonify({'success': False, 'error': 'Assistants must have "Assistant Referee" role'}), 400

        # Validate no duplicate referees
        referee_ids = {referee_id, assistant1_id, assistant2_id}
        if len(referee_ids) != 3:
            return jsonify({'success': False, 'error': 'Cannot assign the same referee to multiple positions'}), 400

        # Check referee availability on match date
        for ref_id in referee_ids:
            existing_assignment = db.session.query(RefereeAssignment).join(Match).filter(
                RefereeAssignment.referee_id == ref_id,
                Match.date == match.date,
                Match.id != match_id  # Exclude current match
            ).first()

            if existing_assignment:
                ref = Referee.query.get(ref_id)
                return jsonify({
                    'success': False,
                    'error': f'Referee {ref.first_name} {ref.last_name} is already assigned to another match on {match.date}'
                }), 400

        # Create new assignments
        assignments = [
            RefereeAssignment(match_id=match_id, referee_id=referee_id, role='Referee'),
            RefereeAssignment(match_id=match_id, referee_id=assistant1_id, role='Assistant Referee'),
            RefereeAssignment(match_id=match_id, referee_id=assistant2_id, role='Assistant Referee')
        ]

        for assignment in assignments:
            db.session.add(assignment)

        db.session.commit()

        return jsonify({'success': True, 'assignments': [a.to_dict() for a in assignments]})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'An error occurred while reassigning referees'}), 500


@app.route('/api/matches/<int:match_id>', methods=['DELETE'])
def delete_match(match_id):
    """Delete match via API"""
    try:
        match = Match.query.get_or_404(match_id)

        # SQLAlchemy will handle cascade deletion of assignments
        db.session.delete(match)
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'An error occurred while deleting the match'}), 500


@app.route('/api/matches/<int:match_id>/available-referees')
def get_available_referees(match_id):
    """Get available referees for a specific match date"""
    match = Match.query.get_or_404(match_id)

    # Get all referees
    all_referees = Referee.query.all()

    # Get referees already assigned on this date
    assigned_referee_ids = db.session.query(RefereeAssignment.referee_id).join(Match).filter(
        Match.date == match.date
    ).all()
    assigned_referee_ids = [ref_id[0] for ref_id in assigned_referee_ids]

    # Filter available referees
    available_referees = [ref for ref in all_referees if ref.id not in assigned_referee_ids]

    main_referees = [ref.to_dict() for ref in available_referees if ref.role == 'Referee']
    assistants = [ref.to_dict() for ref in available_referees if ref.role == 'Assistant Referee']

    return jsonify({
        'mainReferees': main_referees,
        'assistants': assistants
    })


if __name__ == '__main__':
    app.run(debug=True)