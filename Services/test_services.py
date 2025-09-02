import unittest
from datetime import date, timedelta
from Models.database import Database
from Models.entities import Referee, League, Team, Match
from Services.referee_service import RefereeService
from Services.league_service import LeagueService
from Services.match_service import MatchService
from Services.assignment_service import AssignmentService


class TestRefereeService(unittest.TestCase):
    def setUp(self):
        self.db = Database()
        self.service = RefereeService(self.db)

    def test_create_referee_valid(self):
        referee = self.service.create_referee(
            "John", "Doe", "john@example.com", 1, "Referee"
        )
        self.assertEqual(referee.first_name, "John")
        self.assertEqual(referee.last_name, "Doe")
        self.assertEqual(referee.email, "john@example.com")

    def test_create_referee_duplicate_email(self):
        self.service.create_referee("John", "Doe", "john@example.com", 1, "Referee")

        with self.assertRaises(ValueError):
            self.service.create_referee("Jane", "Smith", "john@example.com", 2, "Assistant Referee")

    def test_create_referee_invalid_category(self):
        with self.assertRaises(ValueError):
            self.service.create_referee("John", "Doe", "john@example.com", 3, "Referee")


class TestLeagueService(unittest.TestCase):
    def setUp(self):
        self.db = Database()
        self.service = LeagueService(self.db)

    def test_create_league_with_teams(self):
        team_names = ["Team A", "Team B", "Team C", "Team D"]
        league = self.service.create_league_with_teams("Test League", team_names)

        self.assertEqual(league.name, "Test League")
        self.assertEqual(league.team_count, 4)

        teams = self.db.get_teams_by_league(league.id)
        self.assertEqual(len(teams), 4)

    def test_create_league_invalid_team_count(self):
        team_names = ["Team A", "Team B"]  # Only 2 teams

        with self.assertRaises(ValueError):
            self.service.create_league_with_teams("Test League", team_names)


class TestMatchService(unittest.TestCase):
    def setUp(self):
        self.db = Database()
        self.match_service = MatchService(self.db)
        self.league_service = LeagueService(self.db)

        # Create test data
        self.league = self.league_service.create_league_with_teams(
            "Test League", ["Team A", "Team B", "Team C", "Team D"]
        )
        self.teams = self.db.get_teams_by_league(self.league.id)

    def test_create_match_valid(self):
        match_date = (date.today() + timedelta(days=1)).isoformat()
        match = self.match_service.create_match(
            self.teams[0].id, self.teams[1].id, match_date, self.league.id
        )

        self.assertEqual(match.team1_id, self.teams[0].id)
        self.assertEqual(match.team2_id, self.teams[1].id)
        self.assertEqual(match.date, match_date)

    def test_create_match_same_team(self):
        match_date = (date.today() + timedelta(days=1)).isoformat()

        with self.assertRaises(ValueError):
            self.match_service.create_match(
                self.teams[0].id, self.teams[0].id, match_date, self.league.id
            )


class TestAssignmentService(unittest.TestCase):
    def setUp(self):
        self.db = Database()
        self.assignment_service = AssignmentService(self.db)
        self.referee_service = RefereeService(self.db)
        self.league_service = LeagueService(self.db)
        self.match_service = MatchService(self.db)

        # Create test data
        self.referee = self.referee_service.create_referee("John", "Doe", "john@example.com", 1, "Referee")
        self.assistant1 = self.referee_service.create_referee("Jane", "Smith", "jane@example.com", 1,
                                                              "Assistant Referee")
        self.assistant2 = self.referee_service.create_referee("Bob", "Wilson", "bob@example.com", 2,
                                                              "Assistant Referee")

        self.league = self.league_service.create_league_with_teams(
            "Test League", ["Team A", "Team B", "Team C", "Team D"]
        )
        teams = self.db.get_teams_by_league(self.league.id)

        match_date = (date.today() + timedelta(days=1)).isoformat()
        self.match = self.match_service.create_match(
            teams[0].id, teams[1].id, match_date, self.league.id
        )

    def test_assign_referees_valid(self):
        assignments = self.assignment_service.assign_referees_to_match(
            self.match.id, self.referee.id, self.assistant1.id, self.assistant2.id
        )

        self.assertEqual(len(assignments), 3)
        self.assertEqual(assignments[0].role, "Referee")
        self.assertEqual(assignments[1].role, "Assistant Referee")
        self.assertEqual(assignments[2].role, "Assistant Referee")

    def test_assign_referees_duplicate(self):
        with self.assertRaises(ValueError):
            self.assignment_service.assign_referees_to_match(
                self.match.id, self.referee.id, self.referee.id, self.assistant2.id
            )


if __name__ == '__main__':
    unittest.main()