"""
Data Validator

Domain-level validation and data cleaning logic.
Provides robust data validation and normalization for country information.

Interview Note: Centralized validation logic demonstrates 
Single Responsibility Principle and makes testing easier.
"""

import re
from typing import Tuple, Optional

from ..exceptions import InvalidPopulationError, InvalidCountryNameError


class DataValidator:
    """
    Validates and cleans raw data before creating domain entities.
    
    Validation Features:
    - Country name cleaning and normalization
    - Population parsing with multiple format support
    - parse_population: Lines 150-192
    
    Interview Note: Static methods allow usage without instantiation,
    as validators are stateless. Could be enhanced with caching if needed.
    """
    
    @staticmethod
    def clean_country_name(raw_name: str) -> str:
        """
        Clean country name by removing footnotes and HTML formatting.
        Cleans and normalizes country names by removing Wikipedia artifacts.
        Handles footnotes, HTML tags, and formatting inconsistencies.

        
        Handles:
        - HTML tags (<sup>, <sub>, etc.)
        - Footnote markers ([1], [a], [note 1])
        - Superscript markers (^)
        - Extra whitespace
        
        Args:
            raw_name: Raw country name from HTML
        
        Returns:
            Cleaned country name
        
        Raises:
            InvalidCountryNameError: If cleaned name is empty
        
        Examples:
            >>> DataValidator.clean_country_name("India[1]")
            'India'
            >>> DataValidator.clean_country_name("China<sup>a</sup>")
            'China'
        
        Interview Note: Regex patterns handle Wikipedia's various 
        footnote formats. Each pattern targets specific markup type.
        """
        # Remove HTML tags AND their content (e.g., <sup>1</sup> -> empty)
        # Pattern: <tag>anything</tag>
        # DOTALL flag allows matching across newlines
        name = re.sub(r'<sup[^>]*>.*?</sup>', '', raw_name, flags=re.DOTALL)
        name = re.sub(r'<sub[^>]*>.*?</sub>', '', name, flags=re.DOTALL)
        
        # Remove any remaining HTML tags (opening/closing/self-closing)
        # Pattern: < followed by anything, followed by >
        name = re.sub(r'<[^>]+>', '', name)
        
        # Remove footnote markers: [1], [a], [note 1], etc.
        # Pattern: [ followed by anything, followed by ]
        # Non-greedy (.*?) prevents matching multiple brackets
        name = re.sub(r'\[.*?\]', '', name)
        
        # Remove any remaining superscript or subscript markers
        # Pattern: ^ followed by anything until whitespace
        name = re.sub(r'\^.*?', '', name)
        
        # Strip whitespace and validate
        cleaned = name.strip()
        if not cleaned:
            raise InvalidCountryNameError(f"Cleaned name is empty from: '{raw_name}'")
        
        return cleaned
    
    @staticmethod
    def parse_population(pop_str: str) -> int:
        """
        Parse population string to integer, handling various number formats.
        Parses population strings with support for multiple number formats.
        Handles comma/space separators and validates positive numbers.

        
        Handles formats:
        - "1,234,567" (comma-separated)
        - "1 234 567" (space-separated)
        - "1\xa0234\xa0567" (non-breaking space - Unicode \xa0)
        - Mixed formats: "1,234 567"
        - Numbers with text: "1,234,567 (17.3%)"
        
        Args:
            pop_str: Population string from HTML
        
        Returns:
            Population as positive integer
        
        Raises:
            InvalidPopulationError: If string cannot be parsed or is invalid
        
        Examples:
            >>> DataValidator.parse_population("1,234,567")
            1234567
            >>> DataValidator.parse_population("1 234 567")
            1234567
        
        Interview Note: Demonstrates defensive programming - 
        handles multiple input formats, validates output,
        provides clear error messages for debugging.
        """
        # First, extract the first number (before any parentheses or percentage)
        # Pattern: optional minus sign followed by digits with common separators
        # Matches: 1,234,567 or 1 234 567 or 1\xa0234\xa0567 or -1000
        match = re.search(r'-?[\d,\s\xa0]+', pop_str)
        if match:
            number_str = match.group()
        else:
            raise InvalidPopulationError(f"Cannot find number in: '{pop_str}'")
        
        # Remove all whitespace, commas, and non-breaking spaces
        # Non-breaking space is \xa0 in Unicode (common in HTML)
        cleaned = number_str.replace(',', '').replace(' ', '').replace('\xa0', '')
        
        # Remove any other non-digit characters except minus sign
        # This catches edge cases like accidental letters but preserves negative sign
        cleaned = re.sub(r'[^\d-]', '', cleaned)
        
        if not cleaned:
            raise InvalidPopulationError(f"Cannot parse population from: '{pop_str}'")
        
        try:
            population = int(cleaned)
            
            # Validate result is positive
            # Zero and negative populations are invalid
            if population <= 0:
                raise InvalidPopulationError(f"Population must be positive: {population}")
            
            return population
            
        except (ValueError, OverflowError) as e:
            # ValueError: string not convertible to int
            # OverflowError: number too large for int (rare but possible)
            raise InvalidPopulationError(
                f"Invalid population value '{pop_str}': {e}"
            ) from e
    
    @staticmethod
    def validate_country_data(
        raw_name: str,
        raw_population: str,
        raw_date: str
    ) -> Tuple[str, int, str]:
        """
        Validate and clean complete country data in one call.
        
        New method combining all validations for convenience.
        Returns cleaned/validated data or raises appropriate exception.
        
        Args:
            raw_name: Raw country name from HTML
            raw_population: Raw population string from HTML
            raw_date: Raw date string from HTML
        
        Returns:
            Tuple of (cleaned_name, parsed_population, cleaned_date)
        
        Raises:
            InvalidCountryNameError: If name is invalid
            InvalidPopulationError: If population is invalid
        
        Interview Note: Facade method that simplifies validation 
        for callers while maintaining single responsibility for 
        each individual validator.
        """
        name = DataValidator.clean_country_name(raw_name)
        population = DataValidator.parse_population(raw_population)
        date = raw_date.strip() if raw_date and raw_date.strip() else "N/A"
        
        return name, population, date
    
    @staticmethod
    def clean_date(raw_date: str) -> str:
        """
        Clean and validate date string.
        
        Args:
            raw_date: Raw date string from HTML
        
        Returns:
            Cleaned date string or "N/A" if empty
        
        Examples:
            >>> DataValidator.clean_date("  2024  ")
            '2024'
            >>> DataValidator.clean_date("")
            'N/A'
        """
        if not raw_date or not raw_date.strip():
            return "N/A"
        return raw_date.strip()