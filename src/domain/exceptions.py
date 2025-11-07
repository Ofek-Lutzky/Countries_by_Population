"""
Domain Exceptions

Custom exceptions for domain-level errors.
These represent violations of business rules or domain invariants.
"""


class DomainException(Exception):
    """Base exception for all domain-level errors"""
    pass


class ValidationError(DomainException):
    """Raised when domain validation fails"""
    pass


class InvalidCountryDataError(ValidationError):
    """Raised when country data is invalid"""
    pass


class InvalidPopulationError(ValidationError):
    """Raised when population data is invalid"""
    pass


class InvalidCountryNameError(ValidationError):
    """Raised when country name is invalid"""
    pass