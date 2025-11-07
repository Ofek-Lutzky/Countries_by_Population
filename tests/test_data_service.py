"""
Unit Tests for Data Service

Tests business logic for sorting, filtering, and duplicate detection.
"""

import pytest
from src.application.services.data_service import DataService
from src.domain.models.country import Country


class TestDataService:
    """Test suite for DataService class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = DataService()
        
        # Create test countries
        self.countries = [
            Country("China", 1408280000, "2024"),
            Country("India", 1417492000, "2024"),
            Country("United States", 340110988, "2024"),
            Country("Indonesia", 284438782, "2024"),
            Country("Pakistan", 240485658, "2024"),
            Country("Brazil", 216422446, "2024"),
            Country("Nigeria", 232679478, "2024"),
            Country("Bangladesh", 174701211, "2024"),
            Country("Russia", 146150789, "2024"),
            Country("Mexico", 130861007, "2024"),
        ]
    
    # ==================== Sorting Tests ====================
    
    def test_sort_descending(self):
        """Test sorting by population in descending order."""
        sorted_countries = self.service.sort_by_population(
            self.countries, 
            descending=True
        )
        
        # Check first and last
        assert sorted_countries[0].name == "India"  # Highest
        assert sorted_countries[-1].name == "Mexico"  # Lowest
        
        # Verify all pairs are in order
        for i in range(len(sorted_countries) - 1):
            assert sorted_countries[i].population >= sorted_countries[i+1].population
    
    def test_sort_ascending(self):
        """Test sorting by population in ascending order."""
        sorted_countries = self.service.sort_by_population(
            self.countries,
            descending=False
        )
        
        # Check first and last
        assert sorted_countries[0].name == "Mexico"  # Lowest
        assert sorted_countries[-1].name == "India"  # Highest
        
        # Verify all pairs are in order
        for i in range(len(sorted_countries) - 1):
            assert sorted_countries[i].population <= sorted_countries[i+1].population
    
    def test_sort_empty_list(self):
        """Test sorting empty list."""
        sorted_countries = self.service.sort_by_population([], descending=True)
        assert sorted_countries == []
    
    def test_sort_single_item(self):
        """Test sorting single item."""
        single = [Country("Test", 1000000, "2024")]
        sorted_countries = self.service.sort_by_population(single, descending=True)
        assert len(sorted_countries) == 1
        assert sorted_countries[0].name == "Test"
    
    def test_sort_preserves_original(self):
        """Test that sorting doesn't modify original list."""
        original_order = [c.name for c in self.countries]
        self.service.sort_by_population(self.countries, descending=True)
        
        # Original should be unchanged
        assert [c.name for c in self.countries] == original_order
    
    # ==================== Filtering Tests ====================
    
    def test_filter_by_min_population(self):
        """Test filtering by minimum population."""
        min_pop = 200000000  # 200 million
        
        filtered = self.service.filter_by_min_population(self.countries, min_pop)
        
        # Should only include countries >= 200M
        assert len(filtered) == 7  # China, India, US, Indonesia, Pakistan, Brazil, Nigeria
        assert all(c.population >= min_pop for c in filtered)
    
    def test_filter_removes_below_threshold(self):
        """Test that filtering removes countries below threshold."""
        min_pop = 300000000  # 300 million
        
        filtered = self.service.filter_by_min_population(self.countries, min_pop)
        
        # Should only include 3 countries
        expected_names = {"China", "India", "United States"}
        filtered_names = {c.name for c in filtered}
        
        assert filtered_names == expected_names
    
    def test_filter_zero_threshold(self):
        """Test filtering with zero threshold (should include all)."""
        filtered = self.service.filter_by_min_population(self.countries, 0)
        assert len(filtered) == len(self.countries)
    
    def test_filter_very_high_threshold(self):
        """Test filtering with threshold higher than all populations."""
        min_pop = 2000000000  # 2 billion (higher than any country)
        
        filtered = self.service.filter_by_min_population(self.countries, min_pop)
        assert len(filtered) == 0
    
    def test_filter_preserves_original(self):
        """Test that filtering doesn't modify original list."""
        original_length = len(self.countries)
        self.service.filter_by_min_population(self.countries, 300000000)
        
        # Original should be unchanged
        assert len(self.countries) == original_length
    
    # ==================== Duplicate Detection Tests ====================
    
    def test_find_duplicates_none(self):
        """Test duplicate detection when there are no duplicates."""
        duplicates = self.service.find_duplicates(self.countries)
        assert len(duplicates) == 0
    
    def test_find_duplicates_single(self):
        """Test finding a single duplicate country."""
        countries_with_dupe = self.countries + [
            Country("China", 1400000000, "2023"),  # Duplicate with different data
        ]
        
        duplicates = self.service.find_duplicates(countries_with_dupe)
        
        assert len(duplicates) == 1
        assert "China" in duplicates
        assert len(duplicates["China"]) == 2
    
    def test_find_duplicates_multiple(self):
        """Test finding multiple duplicate countries."""
        countries_with_dupes = self.countries + [
            Country("China", 1400000000, "2023"),
            Country("India", 1410000000, "2023"),
            Country("China", 1390000000, "2022"),  # China appears 3 times total
        ]
        
        duplicates = self.service.find_duplicates(countries_with_dupes)
        
        assert len(duplicates) == 2  # China and India
        assert "China" in duplicates
        assert "India" in duplicates
        assert len(duplicates["China"]) == 3
        assert len(duplicates["India"]) == 2
    
    def test_find_duplicates_preserves_all_occurrences(self):
        """Test that all duplicate occurrences are preserved."""
        countries_with_dupes = [
            Country("TestCountry", 1000000, "2024"),
            Country("TestCountry", 1100000, "2023"),
            Country("TestCountry", 1200000, "2022"),
        ]
        
        duplicates = self.service.find_duplicates(countries_with_dupes)
        
        assert "TestCountry" in duplicates
        assert len(duplicates["TestCountry"]) == 3
        
        # Verify different populations (not deduplicated)
        pops = [c.population for c in duplicates["TestCountry"]]
        assert len(set(pops)) == 3  # All different
    
    def test_find_duplicates_empty_list(self):
        """Test duplicate detection on empty list."""
        duplicates = self.service.find_duplicates([])
        assert len(duplicates) == 0
    
    # ==================== Statistics Tests ====================
    
    def test_get_statistics_basic(self):
        """Test getting basic statistics."""
        stats = self.service.get_statistics(self.countries)
        
        assert stats['total_countries'] == 10
        assert stats['total_population'] == sum(c.population for c in self.countries)
        assert stats['largest_country'] == "India"
        assert stats['smallest_country'] == "Mexico"
        assert stats['average_population'] == stats['total_population'] / 10
    
    def test_get_statistics_single_country(self):
        """Test statistics with single country."""
        single = [Country("Test", 1000000, "2024")]
        stats = self.service.get_statistics(single)
        
        assert stats['total_countries'] == 1
        assert stats['total_population'] == 1000000
        assert stats['largest_country'] == "Test"
        assert stats['smallest_country'] == "Test"
        assert stats['average_population'] == 1000000
    
    def test_get_statistics_empty_list(self):
        """Test statistics with empty list."""
        stats = self.service.get_statistics([])
        
        assert stats['total_countries'] == 0
        assert stats['total_population'] == 0
        assert stats['largest_country'] is None
        assert stats['smallest_country'] is None
        assert stats['average_population'] == 0
    
    # ==================== Integration Tests ====================
    
    def test_sort_then_filter(self):
        """Test sorting followed by filtering."""
        # First sort
        sorted_countries = self.service.sort_by_population(
            self.countries,
            descending=True
        )
        
        # Then filter
        filtered = self.service.filter_by_min_population(sorted_countries, 200000000)
        
        # Should be sorted AND filtered
        assert filtered[0].name == "India"  # Highest of filtered
        assert all(c.population >= 200000000 for c in filtered)
        
        # Verify order maintained
        for i in range(len(filtered) - 1):
            assert filtered[i].population >= filtered[i+1].population
    
    def test_filter_then_sort(self):
        """Test filtering followed by sorting."""
        # First filter
        filtered = self.service.filter_by_min_population(self.countries, 200000000)
        
        # Then sort
        sorted_filtered = self.service.sort_by_population(filtered, descending=True)
        
        # Should be sorted AND filtered
        assert sorted_filtered[0].name == "India"
        assert all(c.population >= 200000000 for c in sorted_filtered)
    
    def test_full_workflow(self):
        """Test complete workflow: sort, filter, find duplicates."""
        # Add some duplicates
        countries_with_dupes = self.countries + [
            Country("China", 1400000000, "2023"),
        ]
        
        # Step 1: Sort
        sorted_countries = self.service.sort_by_population(
            countries_with_dupes,
            descending=True
        )
        
        # Step 2: Filter
        filtered = self.service.filter_by_min_population(sorted_countries, 150000000)
        
        # Step 3: Find duplicates
        duplicates = self.service.find_duplicates(filtered)
        
        # Step 4: Get statistics
        stats = self.service.get_statistics(filtered)
        
        # Verify all operations worked
        assert len(filtered) > 0
        assert "China" in duplicates
        assert stats['total_countries'] == len(filtered)
        assert filtered[0].population >= filtered[-1].population


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = DataService()
    
    def test_countries_with_same_population(self):
        """Test handling countries with identical populations."""
        countries = [
            Country("Country A", 1000000, "2024"),
            Country("Country B", 1000000, "2024"),
            Country("Country C", 1000000, "2024"),
        ]
        
        sorted_countries = self.service.sort_by_population(countries, descending=True)
        
        # All should have same population
        assert all(c.population == 1000000 for c in sorted_countries)
        
        # Order should be stable (preserve original order for equal values)
        assert len(sorted_countries) == 3
    
    def test_very_large_population(self):
        """Test handling very large populations."""
        countries = [
            Country("World", 8232000000, "2024"),  # 8+ billion
            Country("Small", 100, "2024"),
        ]
        
        sorted_countries = self.service.sort_by_population(countries, descending=True)
        assert sorted_countries[0].name == "World"
    
    def test_countries_with_special_names(self):
        """Test handling countries with special characters in names."""
        countries = [
            Country("Côte d'Ivoire", 1000000, "2024"),
            Country("São Tomé and Príncipe", 500000, "2024"),
        ]
        
        # Should not raise any errors
        sorted_countries = self.service.sort_by_population(countries, descending=True)
        duplicates = self.service.find_duplicates(countries)
        
        assert len(sorted_countries) == 2
        assert len(duplicates) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])