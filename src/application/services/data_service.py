"""
Data Service

Service for data processing operations (filtering, sorting, duplicate detection).

Handles data processing, sorting, filtering, and analysis operations.
Provides business logic for country data manipulation.
- filter_by_min_population (lines 585-602)
- Duplicate detection (lines 333-337 in build_dataset)

Interview Note: This is a domain service (operates on domain entities)
but lives in application layer because it coordinates operations.
"""

from typing import List, Dict
from collections import defaultdict
import logging

from ...domain.models.country import Country

logger = logging.getLogger(__name__)


class DataService:
    """
    Service for processing country data.
    
    Pure business logic operations on collections of Country entities.
    No external dependencies - just transforms and analyzes data.
    
    Interview Points:
    - Stateless service (no instance variables)
    - Pure functions (no side effects)
    - Easy to test (deterministic inputs/outputs)
    - Single Responsibility (only data operations)
    """
    
    def sort_by_population(
        self,
        countries: List[Country],
        descending: bool = True
    ) -> List[Country]:
        """
        Sort countries by population.
        
        Sorts countries by population with configurable direction.
        Enhanced with flexible sort direction parameter.
        
        Args:
            countries: List of Country entities to sort
            descending: If True, largest first (default). If False, smallest first.
        
        Returns:
            New sorted list (original list unchanged)
        
        Interview Note: Returns new list rather than modifying in place.
        This follows functional programming principles and prevents
        unexpected side effects.
        """
        sorted_countries = sorted(
            countries,
            key=lambda c: c.population,
            reverse=descending
        )
        
        logger.debug(
            f"Sorted {len(countries)} countries by population "
            f"({'descending' if descending else 'ascending'})"
        )
        
        return sorted_countries
    
    def filter_by_min_population(
        self,
        countries: List[Country],
        min_population: int
    ) -> List[Country]:
        """
        Filter countries by minimum population threshold.
        
        Filters countries by minimum population threshold.
        Includes comprehensive logging for transparency.
        
        Args:
            countries: List of Country entities
            min_population: Minimum population threshold (inclusive)
        
        Returns:
            Filtered list containing only countries with population >= threshold
        
        Interview Note: List comprehension is Pythonic and efficient.
        Alternative would be filter() with lambda, but comprehension
        is more readable for simple cases.
        """
        filtered = [
            c for c in countries
            if c.population >= min_population
        ]
        
        filtered_count = len(countries) - len(filtered)
        if filtered_count > 0:
            logger.info(
                f"Filtered out {filtered_count} countries "
                f"below threshold of {min_population:,}"
            )
        
        return filtered
    
    def find_duplicates(
        self,
        countries: List[Country]
    ) -> Dict[str, List[Country]]:
        """
        Identify countries appearing multiple times in the dataset.
        
        Identifies countries with multiple population entries.
        Extracted for reusability and clean separation of concerns.
        
        Why duplicates exist: Wikipedia may list same country multiple times
        with different data dates or population estimates.
        
        Args:
            countries: List of Country entities
        
        Returns:
            Dictionary mapping country names to lists of duplicate entries.
            Only includes countries with 2+ occurrences.
        
        Interview Note: Uses defaultdict for cleaner code - no need to
        check if key exists before appending. Returns only actual duplicates
        (>1 occurrence), not all countries.
        """
        # Group countries by name
        name_to_countries = defaultdict(list)
        for country in countries:
            name_to_countries[country.name].append(country)
        
        # Filter to only actual duplicates (2+ occurrences)
        duplicates = {
            name: entries
            for name, entries in name_to_countries.items()
            if len(entries) > 1
        }
        
        if duplicates:
            total_duplicate_entries = sum(len(entries) for entries in duplicates.values())
            logger.info(
                f"Found {len(duplicates)} countries with duplicates "
                f"({total_duplicate_entries} total duplicate entries)"
            )
        
        return duplicates
    
    def get_statistics(self, countries: List[Country]) -> Dict[str, any]:
        """
        Calculate statistics about the dataset.
        
        Calculates comprehensive statistics about the dataset.
        Demonstrates the extensibility of the clean architecture.
        
        Args:
            countries: List of Country entities
        
        Returns:
            Dictionary with statistics:
            - total_countries: Number of countries
            - total_population: Sum of all populations
            - avg_population: Average population
            - max_population: Largest population
            - min_population: Smallest population
            - largest_country: Name of most populous country
            - smallest_country: Name of least populous country
        
        Interview Note: Could be enhanced with median, percentiles, etc.
        This shows how domain services can grow organically.
        """
        if not countries:
            return {
                'total_countries': 0,
                'total_population': 0,
                'average_population': 0,
                'max_population': 0,
                'min_population': 0,
                'largest_country': None,
                'smallest_country': None
            }
        
        populations = [c.population for c in countries]
        largest = max(countries, key=lambda c: c.population)
        smallest = min(countries, key=lambda c: c.population)
        
        return {
            'total_countries': len(countries),
            'total_population': sum(populations),
            'average_population': sum(populations) / len(populations),
            'max_population': max(populations),
            'min_population': min(populations),
            'largest_country': largest.name,
            'smallest_country': smallest.name
        }