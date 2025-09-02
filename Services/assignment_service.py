from typing import List
import re
from Models.entities import RefereeAssignment, Referee
from Models.database import Database


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class AssignmentService:
    def __init__(self, db: Database):
        self.db = db

    def assign_referees_to_match(self, match_id: int, referee_id: int,
                                 assistant1_id: int, assistant2_id: int) -> List[RefereeAssignment]:
        """Assign referees to a match with full validation"""
        # Validate match exists
        match = self.db.get_match_by_id(match_id)
        if not match:
            raise ValueError("Match not found")

        # Validate referees exist and have correct roles
        referee = self.db.get_referee_by_id(referee_id)
        assistant1 = self.db.get_referee_by_id(assistant1_id)
        assistant2 = self.db.get_referee_by_id(assistant2_id)

        if not referee or not assistant1 or not assistant2:
            raise ValueError("One or more referees not found")

        if referee.role != 'Referee':
            raise ValueError("Main referee must have 'Referee' role")

        if assistant1.role != 'Assistant Referee' or assistant2.role != 'Assistant Referee':
            raise ValueError("Assistants must have 'Assistant Referee' role")

        # Validate no duplicate referees
        referee_ids = {referee_id, assistant1_id, assistant2_id}
        if len(referee_ids) != 3:
            raise ValueError("Cannot assign the same referee to multiple positions")

        # Validate availability (no double-booking)
        for ref_id in referee_ids:
            existing_assignments = self.db.get_assignments_by_referee_and_date(ref_id, match.date)
            if existing_assignments:
                ref = self.db.get_referee_by_id(ref_id)
                raise ValueError(
                    f"Referee {ref.first_name} {ref.last_name} is already assigned to another match on {match.date}")

        # Check if match already has assignments
        existing_assignments = self.db.get_assignments_by_match(match_id)
        if existing_assignments:
            raise ValueError("Match already has referee assignments")

        # Create assignments
        assignments = [
            RefereeAssignment(
                id=self.db.get_next_assignment_id(),
                match_id=match_id,
                referee_id=referee_id,
                role='Referee'
            ),
            RefereeAssignment(
                id=self.db.get_next_assignment_id(),
                match_id=match_id,
                referee_id=assistant1_id,
                role='Assistant Referee'
            ),
            RefereeAssignment(
                id=self.db.get_next_assignment_id(),
                match_id=match_id,
                referee_id=assistant2_id,
                role='Assistant Referee'
            )
        ]

        for assignment in assignments:
            self.db.add_assignment(assignment)

        return assignments

    def get_available_referees(self, match_date: str) -> List[Referee]:
        """Get referees available for a specific date"""
        all_referees = self.db.get_all_referees()
        available_referees = []

        for referee in all_referees:
            # Check if referee is already assigned on this date
            assignments = self.db.get_assignments_by_referee_and_date(referee.id, match_date)
            if not assignments:
                available_referees.append(referee)

        return available_referees

    def get_all_assignments(self) -> List[RefereeAssignment]:
        """Get all assignments"""
        return self.db.get_all_assignments()

    def get_assignments_by_match(self, match_id: int) -> List[RefereeAssignment]:
        """Get assignments for a specific match"""
        return self.db.get_assignments_by_match(match_id)

    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email format"""
        if not email or not email.strip():
            raise ValidationError("Email is required")

        email = email.strip().lower()
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not re.match(pattern, email):
            raise ValidationError("Invalid email format")

        return email

    @staticmethod
    def validate_name(name: str, field_name: str) -> str:
        """Validate name fields"""
        if not name or not name.strip():
            raise ValidationError(f"{field_name} is required")

        name = name.strip()
        if len(name) < 2:
            raise ValidationError(f"{field_name} must be at least 2 characters long")

        if len(name) > 50:
            raise ValidationError(f"{field_name} must be less than 50 characters")

        if not re.match(r'^[a-zA-Z\s\-\'\.]+$', name):
            raise ValidationError(f"{field_name} contains invalid characters")

        return name


# Database class methods that were mixed in (these should be in the Database class)
class DatabaseMethods:
    """These methods should be part of your Database class"""

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
        id = self._assignment_counter
        self._assignment_counter += 1
        return id