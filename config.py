import os
from datetime import timedelta


class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database configuration (for future SQLAlchemy integration)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///referee_system.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Application settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# utils/validators.py - Input Validation Utilities
import re
from datetime import datetime
from typing import Optional, List


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class Validators:
    """Collection of validation utilities"""

    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email format and return cleaned email"""
        if not email or not email.strip():
            raise ValidationError("Email is required")

        email = email.strip().lower()
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        return [assignment for assignment in self.assignments.values() if assignment.match_id == match_id]

    def get_assignments_by_referee_and_date(self, referee_id: int, match_date: str) -> List[RefereeAssignment]:
        assignments = []
        for assignment in self.assignments.values():
            if assignment.referee_id == referee_id:
                match = self.get_match_by_id(assignment.match_id)
                if match and match.date == match_date:
                    assignments.append(assignment)
        return assignments

    def get_all_assignments(self) -> List[RefereeAssignment]:
        return list(self.assignments.values())

    def delete_assignments_by_match(self, match_id: int) -> None:
        to_delete = [aid for aid, assignment in self.assignments.items() if assignment.match_id == match_id]
        for aid in to_delete:
            del self.assignments[aid]

    def delete_assignments_by_referee(self, referee_id: int) -> None:
        to_delete = [aid for aid, assignment in self.assignments.items() if assignment.referee_id == referee_id]
        for aid in to_delete:
            del self.assignments[aid]

    def get_next_assignment_id(self) -> int:
        id = self._assignment_counter
        self._assignment_counter += 1
        return id