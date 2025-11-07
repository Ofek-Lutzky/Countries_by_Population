"""
Unit Tests for Parsing Functions

Tests data validation, cleaning, and parsing logic.
"""

import pytest
from src.domain.validators.data_validator import DataValidator
from src.domain.exceptions import InvalidCountryDataError, InvalidCountryNameError, InvalidPopulationError


class TestDataValidator:
    """Test suite for DataValidator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # DataValidator uses static methods, no instance needed
        pass
    
    # ==================== Country Name Cleaning Tests ====================
    
    def test_clean_simple_country_name(self):
        """Test cleaning simple country names without special characters."""
        assert DataValidator.clean_country_name("France") == "France"
        assert DataValidator.clean_country_name("China") == "China"
        assert DataValidator.clean_country_name("United States") == "United States"
    
    def test_clean_country_name_with_footnotes(self):
        """Test removal of various footnote formats."""
        # Numeric footnotes
        assert DataValidator.clean_country_name("France[1]") == "France"
        assert DataValidator.clean_country_name("China[23]") == "China"
        
        # Letter footnotes
        assert DataValidator.clean_country_name("India[a]") == "India"
        assert DataValidator.clean_country_name("Brazil[b]") == "Brazil"
        
        # Named footnotes
        assert DataValidator.clean_country_name("Japan[note 1]") == "Japan"
        assert DataValidator.clean_country_name("Germany[Note 2]") == "Germany"
    
    def test_clean_country_name_with_html_tags(self):
        """Test removal of HTML superscript and subscript tags."""
        # Superscript tags
        assert DataValidator.clean_country_name("China<sup>a</sup>") == "China"
        assert DataValidator.clean_country_name("India<sup>1</sup>") == "India"
        assert DataValidator.clean_country_name("USA<sup>[note 1]</sup>") == "USA"
        
        # Subscript tags
        assert DataValidator.clean_country_name("France<sub>2</sub>") == "France"
    
    def test_clean_country_name_with_mixed_formats(self):
        """Test names with multiple types of artifacts."""
        assert DataValidator.clean_country_name("China<sup>[1]</sup>[a]") == "China"
        assert DataValidator.clean_country_name("United States[1]<sup>a</sup>") == "United States"
    
    def test_clean_country_name_with_whitespace(self):
        """Test handling of extra whitespace."""
        assert DataValidator.clean_country_name("  France  ") == "France"
        assert DataValidator.clean_country_name("United  States") == "United  States"
        assert DataValidator.clean_country_name("\nChina\t") == "China"
    
    def test_clean_empty_country_name(self):
        """Test that empty names raise appropriate error."""
        with pytest.raises(InvalidCountryNameError):
            DataValidator.clean_country_name("")
        
        with pytest.raises(InvalidCountryNameError):
            DataValidator.clean_country_name("   ")
    
    # ==================== Population Parsing Tests ====================
    
    def test_parse_simple_population(self):
        """Test parsing simple numbers without separators."""
        assert DataValidator.parse_population("1234567") == 1234567
        assert DataValidator.parse_population("100") == 100
        assert DataValidator.parse_population("1000000000") == 1000000000
    
    def test_parse_comma_separated_population(self):
        """Test parsing numbers with comma separators (US format)."""
        assert DataValidator.parse_population("1,234,567") == 1234567
        assert DataValidator.parse_population("100,000") == 100000
        assert DataValidator.parse_population("1,000,000,000") == 1000000000
    
    def test_parse_space_separated_population(self):
        """Test parsing numbers with space separators (European format)."""
        assert DataValidator.parse_population("1 234 567") == 1234567
        assert DataValidator.parse_population("100 000") == 100000
        assert DataValidator.parse_population("1 000 000 000") == 1000000000
    
    def test_parse_non_breaking_space_population(self):
        """Test parsing numbers with non-breaking spaces (\\xa0)."""
        # Non-breaking space is \xa0 in Unicode
        assert DataValidator.parse_population("1\xa0234\xa0567") == 1234567
        assert DataValidator.parse_population("100\xa0000") == 100000
    
    def test_parse_mixed_separator_population(self):
        """Test parsing numbers with mixed separators."""
        assert DataValidator.parse_population("1,234 567") == 1234567
        assert DataValidator.parse_population("1 234,567") == 1234567
    
    def test_parse_population_with_percentage(self):
        """Test extracting population from strings with percentages."""
        # Should extract first number, ignore percentage
        assert DataValidator.parse_population("1,234,567 (17.3%)") == 1234567
        assert DataValidator.parse_population("100,000 (1.2%)") == 100000
    
    def test_parse_population_with_text(self):
        """Test extracting population from strings with additional text."""
        assert DataValidator.parse_population("Population: 1,234,567") == 1234567
        assert DataValidator.parse_population("1,234,567 people") == 1234567
    
    def test_parse_zero_population(self):
        """Test that zero population raises error."""
        with pytest.raises(InvalidPopulationError):
            DataValidator.parse_population("0")
    
    def test_parse_negative_population(self):
        """Test that negative population raises error."""
        with pytest.raises(InvalidPopulationError):
            DataValidator.parse_population("-1000")
    
    def test_parse_invalid_population_formats(self):
        """Test that invalid formats raise appropriate errors."""
        with pytest.raises(InvalidPopulationError):
            DataValidator.parse_population("abc")
        
        with pytest.raises(InvalidPopulationError):
            DataValidator.parse_population("")
        
        with pytest.raises(InvalidPopulationError):
            DataValidator.parse_population("N/A")
        
        with pytest.raises(InvalidPopulationError):
            DataValidator.parse_population("unknown")
    
    # ==================== Date Cleaning Tests ====================
    
    def test_clean_simple_date(self):
        """Test cleaning simple date strings."""
        assert DataValidator.clean_date("2024") == "2024"
        assert DataValidator.clean_date("1 July 2024") == "1 July 2024"
        assert DataValidator.clean_date("2024-01-01") == "2024-01-01"
    
    def test_clean_date_with_whitespace(self):
        """Test trimming whitespace from dates."""
        assert DataValidator.clean_date("  2024  ") == "2024"
        assert DataValidator.clean_date("\t2024\n") == "2024"
    
    def test_clean_empty_date(self):
        """Test that empty dates are replaced with default."""
        assert DataValidator.clean_date("") == "N/A"
        assert DataValidator.clean_date("   ") == "N/A"
    
    # ==================== Integration Tests ====================
    
    def test_validate_country_data_success(self):
        """Test successful validation of complete country data."""
        name, population, date = DataValidator.validate_country_data(
            "France[1]",
            "67,000,000",
            "2024"
        )
        
        assert name == "France"
        assert population == 67000000
        assert date == "2024"
    
    def test_validate_country_data_with_complex_input(self):
        """Test validation with complex real-world input."""
        name, population, date = DataValidator.validate_country_data(
            "China<sup>[a]</sup>",
            "1,408,280,000 (17.2%)",
            "1 July 2024"
        )
        
        assert name == "China"
        assert population == 1408280000
        assert date == "1 July 2024"
    
    def test_validate_country_data_invalid_name(self):
        """Test that invalid name raises error."""
        with pytest.raises(InvalidCountryNameError):
            DataValidator.validate_country_data("", "1000000", "2024")
    
    def test_validate_country_data_invalid_population(self):
        """Test that invalid population raises error."""
        with pytest.raises(InvalidPopulationError):
            DataValidator.validate_country_data("France", "invalid", "2024")
    
    # ==================== Edge Cases ====================
    
    def test_very_large_population(self):
        """Test parsing very large populations (like world population)."""
        # World population: ~8 billion
        assert DataValidator.parse_population("8,232,000,000") == 8232000000
    
    def test_very_small_population(self):
        """Test parsing very small populations (small countries)."""
        # Vatican City: ~800 people
        assert DataValidator.parse_population("800") == 800
    
    def test_country_name_with_special_characters(self):
        """Test names with accents and special characters."""
        assert DataValidator.clean_country_name("Côte d'Ivoire") == "Côte d'Ivoire"
        assert DataValidator.clean_country_name("São Tomé") == "São Tomé"
    
    def test_country_name_with_parentheses(self):
        """Test names with parenthetical information."""
        # Should preserve parentheses that aren't footnotes
        result = DataValidator.clean_country_name("China (mainland)")
        assert "China" in result


# ==================== Performance Tests ====================

class TestParsingPerformance:
    """Test parsing performance with realistic data volumes."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # DataValidator uses static methods, no instance needed
        pass
    
    def test_bulk_name_cleaning(self):
        """Test cleaning many country names efficiently."""
        import time
        
        # Generate 1000 test names
        test_names = [f"Country{i}[{i}]<sup>a</sup>" for i in range(1000)]
        
        start = time.time()
        for name in test_names:
            DataValidator.clean_country_name(name)
        duration = time.time() - start
        
        # Should process 1000 names in under 1 second
        assert duration < 1.0, f"Took {duration:.2f}s, should be < 1.0s"
    
    def test_bulk_population_parsing(self):
        """Test parsing many populations efficiently."""
        import time
        
        # Generate 1000 test populations
        test_pops = [f"{i},000,000" for i in range(1, 1001)]
        
        start = time.time()
        for pop in test_pops:
            DataValidator.parse_population(pop)
        duration = time.time() - start
        
        # Should process 1000 populations in under 0.5 seconds
        assert duration < 0.5, f"Took {duration:.2f}s, should be < 0.5s"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])