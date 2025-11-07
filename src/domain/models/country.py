"""
Country Domain Entity

Immutable domain entity representing a country with population data.
Enforces business rules and provides value object behavior.
"""

from dataclasses import dataclass
from typing import Optional

from ..exceptions import InvalidCountryNameError, InvalidPopulationError


@dataclass(frozen=True)
class Country:
    """
    Domain entity representing a country with population data.
    
    Immutable by design (frozen=True) following Domain-Driven Design principles.
    Contains validation logic and business rules.
    
    Attributes:
        name: Country name (cleaned, no footnotes)
        population: Population count (must be non-negative)
        data_date: Date of population data
        flag_path: Optional path to flag image file
    
    Examples:
        >>> country = Country("India", 1_417_492_000, "2024")
        >>> country.format_population()
        '1,417,492,000'
        >>> country.is_large_country()
        True
    """
    
    name: str
    population: int
    data_date: str
    flag_path: Optional[str] = None
    
    def __post_init__(self):
        """
        Validate domain invariants after initialization.
        
        Raises:
            InvalidCountryNameError: If name is empty or whitespace
            InvalidPopulationError: If population is negative
        
        Interview Note: This demonstrates validation at the domain level,
        ensuring invalid entities cannot exist in the system.
        """
        if not self.name or not self.name.strip():
            raise InvalidCountryNameError("Country name cannot be empty")
        
        if self.population < 0:
            raise InvalidPopulationError(
                f"Population must be non-negative, got: {self.population}"
            )
    
    def format_population(self) -> str:
        """
        Format population with thousand separators.
        
        Formats population with thousand separators for display.
        Domain logic encapsulated within the entity.
        
        Returns:
            Formatted population string (e.g., "1,417,492,000")
        
        Interview Note: Moving formatting to the entity follows 
        Single Responsibility Principle - the entity knows how to 
        represent itself.
        """
        return f"{self.population:,}"
    
    def is_large_country(self, threshold: int = 100_000_000) -> bool:
        """
        Business rule: Classify country by population size.
        
        Args:
            threshold: Population threshold for "large" classification
        
        Returns:
            True if population >= threshold
        
        Interview Note: Business rules belong in domain entities.
        This makes the rule explicit and testable.
        """
        return self.population >= threshold
    
    def __str__(self) -> str:
        """String representation for display"""
        return f"{self.name} ({self.format_population()})"
    
    def to_dict(self) -> dict:
        """
        Convert to dictionary for serialization.
        
        Returns:
            Dictionary representation
        
        Interview Note: Provides clean serialization without exposing
        internal structure. Could be enhanced with more sophisticated
        serialization libraries if needed.
        """
        return {
            'name': self.name,
            'population': self.population,
            'data_date': self.data_date,
            'flag_path': self.flag_path
        }