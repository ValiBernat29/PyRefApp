from typing import List, Optional, Dict
from datetime import date, datetime
from Models.entities import Match
from Models.database import Database


class MatchService:
    def __init__(self, db: Database):
        self.db = db

    def create_match(self, team1_id: int, team2_id: int, date: str, league_id: int) -> Match:
        """Create a new match with validation"""
        # Validate teams exist and belong to same league
        team1 = self.db.get_team_by_id(team1_id)
        team2 = self.db.get_team_by_id(team2_id)

        if not team1 or not team2:
            raise ValueError("One or both teams not found")

        if team1.league_id != league_id or team2.league_id != league_id:
            raise ValueError("Teams must belong to the specified league")

        if team1.league_id != team2.league_id:
            raise ValueError("Teams must belong to the same league")

        # Validate date format
        try:
            datetime.fromisoformat(date)
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")

        # Check for duplicate matches on same date
        existing_matches = self.db.get_matches_by_teams_and_date(team1_id, team2_id, date)
        if existing_matches:
            raise ValueError("These teams are already scheduled to play on this date")

        match = Match(
            id=self.db.get_next_match_id(),
            team1_id=team1_id,
            team2_id=team2_id,
            date=date,
            league_id=league_id
        )

        self.db.add_match(match)
        return match

    def get_all_matches(self) -> List[Match]:
        """Get all matches"""
        return self.db.get_all_matches()

    def get_all_matches_with_details(self) -> List[Dict]:
        """Get all matches with team and league details"""
        matches_with_details = []
        for match in self.db.get_all_matches():
            team1 = self.db.get_team_by_id(match.team1_id)
            team2 = self.db.get_team_by_id(match.team2_id)
            league = self.db.get_league_by_id(match.league_id)
            assignments = self.db.get_assignments_by_match(match.id)

            matches_with_details.append({
                'match': match,
                'team1': team1,
                'team2': team2,
                'league': league,
                'assignments': assignments
            })
        return matches_with_details

    def get_match_by_id(self, match_id: int) -> Optional[Match]:
        """Get match by ID"""
        return self.db.get_match_by_id(match_id)

    def get_upcoming_matches(self, limit: int = 5) -> List[Dict]:
        """Get upcoming matches with details"""
        today = date.today().isoformat()
        upcoming = []

        for match in self.db.get_all_matches():
            if match.date >= today:
                team1 = self.db.get_team_by_id(match.team1_id)
                team2 = self.db.get_team_by_id(match.team2_id)
                league = self.db.get_league_by_id(match.league_id)
                assignments = self.db.get_assignments_by_match(match.id)

                upcoming.append({
                    'match': match,
                    'team1': team1,
                    'team2': team2,
                    'league': league,
                    'assignments': assignments
                })

        # Sort by date and limit results
        upcoming.sort(key=lambda x: x['match'].date)
        return upcoming[:limit]

    def delete_match(self, match_id: int) -> None:
        """Delete match and cascade delete assignments"""
        match = self.db.get_match_by_id(match_id)
        if not match:
            raise ValueError("Match not found")

        # Cascade delete assignments
        self.db.delete_assignments_by_match(match_id)
        self.db.delete_match(match_id)