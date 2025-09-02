from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from Models.database import Database
from Services.referee_service import RefereeService
from Services.league_service import LeagueService
from Services.match_service import MatchService
from Services.assignment_service import AssignmentService

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Initialize services
db = Database()
referee_service = RefereeService(db)
league_service = LeagueService(db)
match_service = MatchService(db)
assignment_service = AssignmentService(db)


@app.route('/')
def dashboard():
    """Dashboard with statistics and overview"""
    stats = {
        'referees': len(referee_service.get_all_referees()),
        'leagues': len(league_service.get_all_leagues()),
        'matches': len(match_service.get_all_matches()),
        'assignments': len(assignment_service.get_all_assignments())
    }

    upcoming_matches = match_service.get_upcoming_matches()
    return render_template('dashboard.html', stats=stats, upcoming_matches=upcoming_matches)


# Referee Routes
@app.route('/referees')
def referees():
    """Referee management page"""
    all_referees = referee_service.get_all_referees()
    return render_template('referees.html', referees=all_referees)


@app.route('/api/referees', methods=['POST'])
def add_referee():
    """Add new referee via API"""
    data = request.get_json()
    try:
        referee = referee_service.create_referee(
            first_name=data['firstName'],
            last_name=data['lastName'],
            email=data['email'],
            category=int(data['category']),
            role=data['role']
        )
        return jsonify({'success': True, 'referee': referee.__dict__})
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/referees/<int:referee_id>', methods=['DELETE'])
def delete_referee(referee_id):
    """Delete referee via API"""
    try:
        referee_service.delete_referee(referee_id)
        return jsonify({'success': True})
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# League Routes
@app.route('/leagues')
def leagues():
    """League management page"""
    all_leagues = league_service.get_all_leagues_with_teams()
    return render_template('leagues.html', leagues=all_leagues)


@app.route('/api/leagues', methods=['POST'])
def add_league():
    """Add new league with teams via API"""
    data = request.get_json()
    try:
        league = league_service.create_league_with_teams(
            name=data['name'],
            team_names=data['teams']
        )
        return jsonify({'success': True, 'league': league.__dict__})
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/leagues/<int:league_id>/teams', methods=['POST'])
def add_team_to_league(league_id):
    """Add team to existing league via API"""
    data = request.get_json()
    try:
        team = league_service.add_team_to_league(league_id, data['name'])
        return jsonify({'success': True, 'team': team.__dict__})
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# Match Routes
@app.route('/matches')
def matches():
    """Match management page"""
    all_matches = match_service.get_all_matches_with_details()
    all_leagues = league_service.get_all_leagues()
    return render_template('matches.html', matches=all_matches, leagues=all_leagues)


@app.route('/api/matches', methods=['POST'])
def add_match():
    """Add new match via API"""
    data = request.get_json()
    try:
        match = match_service.create_match(
            team1_id=int(data['team1Id']),
            team2_id=int(data['team2Id']),
            date=data['date'],
            league_id=int(data['leagueId'])
        )
        return jsonify({'success': True, 'match': match.__dict__})
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/leagues/<int:league_id>/teams')
def get_league_teams(league_id):
    """Get teams for a specific league"""
    teams = league_service.get_teams_by_league(league_id)
    return jsonify([team.__dict__ for team in teams])


# Assignment Routes
@app.route('/api/matches/<int:match_id>/assign', methods=['POST'])
def assign_referees_to_match(match_id):
    """Assign referees to a match"""
    data = request.get_json()
    try:
        assignments = assignment_service.assign_referees_to_match(
            match_id=match_id,
            referee_id=int(data['refereeId']),
            assistant1_id=int(data['assistant1Id']),
            assistant2_id=int(data['assistant2Id'])
        )
        return jsonify({'success': True, 'assignments': [a.__dict__ for a in assignments]})
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/matches/<int:match_id>/available-referees')
def get_available_referees(match_id):
    """Get available referees for a specific match date"""
    match = match_service.get_match_by_id(match_id)
    if not match:
        return jsonify({'error': 'Match not found'}), 404

    available_refs = assignment_service.get_available_referees(match.date)
    main_referees = [ref.__dict__ for ref in available_refs if ref.role == 'Referee']
    assistants = [ref.__dict__ for ref in available_refs if ref.role == 'Assistant Referee']

    return jsonify({
        'mainReferees': main_referees,
        'assistants': assistants
    })


if __name__ == '__main__':
    # Initialize with sample data
    db.init_sample_data()
    app.run(debug=True)


