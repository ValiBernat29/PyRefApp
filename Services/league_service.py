from typing import List, Optional, Dict
from Models.entities import League, Team
from Models.database import Database


class LeagueService:
    def __init__(self, db: Database):
        self.db = db

    def create_league_with_teams(self, name: str, team_names: List[str]) -> League:
        """Create a new league with its teams"""
        # Validate league name uniqueness
        if self.db.get_league_by_name(name):
            raise ValueError(f"League with name '{name}' already exists")

        # Validate team count
        team_count = len(team_names)
        if not (4 <= team_count <= 6):
            raise ValueError("League must have between 4 and 6 teams")

        # Validate team names
        clean_team_names = []
        for team_name in team_names:
            if not team_name.strip():
                raise ValueError("Team name cannot be empty")
            clean_name = team_name.strip()
            if clean_name in clean_team_names:
                raise ValueError(f"Duplicate team name: {clean_name}")
            clean_team_names.append(clean_name)

        # Create league
        league = League(
            id=self.db.get_next_league_id(),
            name=name.strip(),
            team_count=team_count
        )
        self.db.add_league(league)

        # Create teams
        for team_name in clean_team_names:
            team = Team(
                id=self.db.get_next_team_id(),
                name=team_name,
                league_id=league.id
            )
            self.db.add_team(team)

        return league

    def add_team_to_league(self, league_id: int, team_name: str) -> Team:
        """Add a team to an existing league"""
        league = self.db.get_league_by_id(league_id)
        if not league:
            raise ValueError("League not found")

        # Check if league is full
        current_teams = self.db.get_teams_by_league(league_id)
        if len(current_teams) >= league.team_count:
            raise ValueError(f"League already has maximum number of teams ({league.team_count})")

        # Validate team name uniqueness within league
        clean_name = team_name.strip()
        if not clean_name:
            raise ValueError("Team name cannot be empty")

        if self.db.get_team_by_name_and_league(clean_name, league_id):
            raise ValueError(f"Team '{clean_name}' already exists in this league")

        team = Team(
            id=self.db.get_next_team_id(),
            name=clean_name,
            league_id=league_id
        )
        self.db.add_team(team)
        return team

    def get_all_leagues(self) -> List[League]:
        """Get all leagues"""
        return self.db.get_all_leagues()

    def get_all_leagues_with_teams(self) -> List[Dict]:
        """Get all leagues with their teams"""
        leagues_with_teams = []
        for league in self.db.get_all_leagues():
            teams = self.db.get_teams_by_league(league.id)
            leagues_with_teams.append({
                'league': league,
                'teams': teams
            })
        return leagues_with_teams

    def get_teams_by_league(self, league_id: int) -> List[Team]:
        """Get all teams in a league"""
        return self.db.get_teams_by_league(league_id)