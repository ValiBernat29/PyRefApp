from typing import List, Optional
from Models.entities import Referee
from Models.database import Database


class RefereeService:
    def __init__(self, db: Database):
        self.db = db

    def create_referee(self, first_name: str, last_name: str, email: str, category: int, role: str) -> Referee:
        """Create a new referee with validation"""
        # Validate email uniqueness
        if self.db.get_referee_by_email(email):
            raise ValueError(f"Referee with email {email} already exists")

        # Validate inputs
        if not first_name.strip():
            raise ValueError("First name is required")
        if not last_name.strip():
            raise ValueError("Last name is required")
        if not email.strip():
            raise ValueError("Email is required")

        referee = Referee(
            id=self.db.get_next_referee_id(),
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            email=email.strip().lower(),
            category=category,
            role=role
        )

        self.db.add_referee(referee)
        return referee

    def get_all_referees(self) -> List[Referee]:
        """Get all referees"""
        return self.db.get_all_referees()

    def get_referee_by_id(self, referee_id: int) -> Optional[Referee]:
        """Get referee by ID"""
        return self.db.get_referee_by_id(referee_id)

    def delete_referee(self, referee_id: int) -> None:
        """Delete referee and cascade delete assignments"""
        referee = self.db.get_referee_by_id(referee_id)
        if not referee:
            raise ValueError("Referee not found")

        # Cascade delete assignments
        self.db.delete_assignments_by_referee(referee_id)
        self.db.delete_referee(referee_id)

    def get_referees_by_role(self, role: str) -> List[Referee]:
        """Get referees filtered by role"""
        return [ref for ref in self.get_all_referees() if ref.role == role]