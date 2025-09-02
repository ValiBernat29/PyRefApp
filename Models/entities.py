# models/entities.py - Domain Models
from dataclasses import dataclass
from typing import Optional
from datetime import date


@dataclass
class Referee:
    id: int
    first_name: str
    last_name: str
    email: str
    category: int  # 1 or 2
    role: str  # 'Referee' or 'Assistant Referee'

    def __post_init__(self):
        if self.category not in [1, 2]:
            raise ValueError("Category must be 1 or 2")
        if self.role not in ['Referee', 'Assistant Referee']:
            raise ValueError("Role must be 'Referee' or 'Assistant Referee'")


@dataclass
class League:
    id: int
    name: str
    team_count: int

    def __post_init__(self):
        if not (4 <= self.team_count <= 6):
            raise ValueError("Team count must be between 4 and 6")


@dataclass
class Team:
    id: int
    name: str
    league_id: int


@dataclass
class Match:
    id: int
    team1_id: int
    team2_id: int
    date: str  # ISO date string
    league_id: int

    def __post_init__(self):
        if self.team1_id == self.team2_id:
            raise ValueError("Team cannot play against itself")


@dataclass
class RefereeAssignment:
    id: int
    match_id: int
    referee_id: int
    role: str  # 'Referee' or 'Assistant Referee'