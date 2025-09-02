from typing import List, Optional, Dict
from datetime import date, timedelta
from Models.entities import Referee, League, Team, Match, RefereeAssignment


class Database:
    """In-memory database simulation. In production, replace with SQLAlchemy or similar ORM."""

    def __init__(self):
        self.referees: Dict[int, Referee] = {}
        self.leagues: Dict[int, League] = {}
        self.teams: Dict[int, Team] = {}
        self.matches: Dict[int, Match] = {}
        self.assignments: Dict[int, RefereeAssignment] = {}

        self._referee_counter = 1
        self._league_counter = 1
        self._team_counter = 1
        self._match_counter = 1
        self._assignment_counter = 1

    def init_sample_data(self):
        """Initialize database with sample data for testing"""
        # Sample referees
        sample_referees = [
            ('John', 'Smith', 'john.smith@email.com', 1, 'Referee'),
            ('Maria', 'Garcia', 'maria.garcia@email.com', 1, 'Assistant Referee'),
            ('David', 'Wilson', 'david.wilson@email.com', 2, 'Assistant Referee'),
            ('Sarah', 'Johnson', 'sarah.johnson@email.com', 1, 'Referee'),
            ('Michael', 'Brown', 'michael.brown@email.com', 2, 'Assistant Referee'),
        ]

        for first_name, last_name, email, category, role in sample_referees:
            self.add_referee(Referee(
                id=self._referee_counter,
                first_name=first_name,
                last_name=last_name,
                email=email,
                category=category,
                role=role
            ))
            self._referee_counter += 1

        # Sample league
        league = League(id=self._league_counter, name='Premier Division', team_count=4)
        self.add_league(league)
        league_id = self._league_counter
        self._league_counter += 1

        # Sample teams
        team_names = ['Arsenal FC', 'Chelsea FC', 'Liverpool FC', 'Manchester United']
        for name in team_names:
            team = Team(id=self._team_counter, name=name, league_id=league_id)
            self.add_team(team)
            self._team_counter += 1

        # Sample match
        today = date.today()
        match_date = (today + timedelta(days=7)).isoformat()
        match = Match(
            id=self._match_counter,
            team1_id=1,
            team2_id=2,
            date=match_date,
            league_id=league_id
        )
        self.add_match(match)
        self._match_counter += 1

    # Referee operations
    def add_referee(self, referee: Referee) -> None:
        self.referees[referee.id] = referee

    def get_referee_by_id(self, referee_id: int) -> Optional[Referee]:
        return self.referees.get(referee_id)

    def get_referee_by_email(self, email: str) -> Optional[Referee]:
        return next((ref for ref in self.referees.values() if ref.email == email), None)

    def get_all_referees(self) -> List[Referee]:
        return list(self.referees.values())

    def delete_referee(self, referee_id: int) -> None:
        if referee_id in self.referees:
            del self.referees[referee_id]

    def get_next_referee_id(self) -> int:
        id = self._referee_counter
        self._referee_counter += 1
        return id

    # League operations
    def add_league(self, league: League) -> None:
        self.leagues[league.id] = league

    def get_league_by_id(self, league_id: int) -> Optional[League]:
        return self.leagues.get(league_id)

    def get_league_by_name(self, name: str) -> Optional[League]:
        return next((league for league in self.leagues.values() if league.name == name), None)

    def get_all_leagues(self) -> List[League]:
        return list(self.leagues.values())

    def get_next_league_id(self) -> int:
        id = self._league_counter
        self._league_counter += 1
        return id

    # Team operations
    def add_team(self, team: Team) -> None:
        self.teams[team.id] = team

    def get_team_by_id(self, team_id: int) -> Optional[Team]:
        return self.teams.get(team_id)

    def get_teams_by_league(self, league_id: int) -> List[Team]:
        return [team for team in self.teams.values() if team.league_id == league_id]

    def get_team_by_name_and_league(self, name: str, league_id: int) -> Optional[Team]:
        return next((team for team in self.teams.values()
                     if team.name == name and team.league_id == league_id), None)

    def delete_team(self, team_id: int) -> None:
        if team_id in self.teams:
            del self.teams[team_id]

    def get_next_team_id(self) -> int:
        id = self._team_counter
        self._team_counter += 1
        return id

    # Match operations
    def add_match(self, match: Match) -> None:
        self.matches[match.id] = match

    def get_match_by_id(self, match_id: int) -> Optional[Match]:
        return self.matches.get(match_id)

    def get_all_matches(self) -> List[Match]:
        return list(self.matches.values())

    def get_matches_by_date(self, match_date: str) -> List[Match]:
        return [match for match in self.matches.values() if match.date == match_date]

    def get_matches_by_teams_and_date(self, team1_id: int, team2_id: int, match_date: str) -> List[Match]:
        return [match for match in self.matches.values()
                if match.date == match_date and
                ((match.team1_id == team1_id and match.team2_id == team2_id) or
                 (match.team1_id == team2_id and match.team2_id == team1_id))]

    def delete_match(self, match_id: int) -> None:
        if match_id in self.matches:
            del self.matches[match_id]

    def get_next_match_id(self) -> int:
        id = self._match_counter
        self._match_counter += 1
        return id

    # Assignment operations
    def add_assignment(self, assignment: RefereeAssignment) -> None:
        self.assignments[assignment.id] = assignment

    def get_assignments_by_match(self, match_id: int) -> List[RefereeAssignment]:
        """Get assignments for a specific match"""
        return [assignment for assignment in self.assignments.values() if assignment.match_id == match_id]

    def get_assignments_by_referee_and_date(self, referee_id: int, match_date: str) -> List[RefereeAssignment]:
        """Get assignments for a referee on a specific date"""
        assignments = []
        for assignment in self.assignments.values():
            if assignment.referee_id == referee_id:
                match = self.get_match_by_id(assignment.match_id)
                if match and match.date == match_date:
                    assignments.append(assignment)
        return assignments

    def get_all_assignments(self) -> List[RefereeAssignment]:
        """Get all assignments"""
        return list(self.assignments.values())

    def delete_assignments_by_match(self, match_id: int) -> None:
        """Delete all assignments for a specific match"""
        to_delete = [aid for aid, assignment in self.assignments.items() if assignment.match_id == match_id]
        for aid in to_delete:
            del self.assignments[aid]

    def delete_assignments_by_referee(self, referee_id: int) -> None:
        """Delete all assignments for a specific referee"""
        to_delete = [aid for aid, assignment in self.assignments.items() if assignment.referee_id == referee_id]
        for aid in to_delete:
            del self.assignments[aid]

    def get_next_assignment_id(self) -> int:
        """Get the next assignment ID"""
        assignment_id = self._assignment_counter
        self._assignment_counter += 1
        return assignment_id