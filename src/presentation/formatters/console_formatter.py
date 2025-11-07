"""
Console Formatter

Formats country data for console output.
Provides clean, readable table formatting for terminal display.
"""

from typing import List, Dict

from ...domain.models.country import Country


class ConsoleFormatter:
    """
    Format country data for console display.
    
    Features:
    - Clean table formatting with proper alignment
    - Duplicate detection and marking
    - Population formatting with thousand separators
    - Returns string for testability instead of direct printing
    - Separated formatting logic from I/O
    - Works with Country entities instead of dicts
    """
    
    def format(
        self,
        countries: List[Country],
        duplicates: Dict[str, List[Country]] = None
    ) -> str:
        """
        Format countries for console display.
        
        Args:
            countries: Sorted list of countries
            duplicates: Optional map of duplicate country entries
        
        Returns:
            Formatted string ready for printing
        """
        duplicates = duplicates or {}
        lines = []
        
        # Header section
        lines.append("\n" + "=" * 80)
        lines.append("COUNTRIES BY POPULATION (Descending Order)")
        lines.append("=" * 80)
        lines.append(f"Total entries: {len(countries)}\n")
        
        # Main listing
        for rank, country in enumerate(countries, 1):
            duplicate_marker = "*" if country.name in duplicates else " "
            
            line = (
                f"{rank:3d}. {duplicate_marker} "
                f"{country.name:40s} "
                f"{country.format_population():>15s}  "
                f"({country.data_date})"
            )
            lines.append(line)
        
        # Duplicates section
        if duplicates:
            lines.extend(self._format_duplicates_section(duplicates))
        
        return "\n".join(lines)
    
    def _format_duplicates_section(
        self,
        duplicates: Dict[str, List[Country]]
    ) -> List[str]:
        """
        Format duplicates section.
        
        Formats duplicate countries section with detailed breakdown.
        """
        lines = []
        lines.append("\n" + "=" * 80)
        lines.append("COUNTRIES WITH MULTIPLE ENTRIES")
        lines.append("=" * 80)
        lines.append(
            f"Found {len(duplicates)} countries with multiple occurrences:\n"
        )
        
        for country_name in sorted(duplicates.keys()):
            entries = duplicates[country_name]
            lines.append(f"\n{country_name} - {len(entries)} occurrences:")
            
            for i, entry in enumerate(entries, 1):
                lines.append(
                    f"  {i}. Population: {entry.format_population():>15s}  "
                    f"Date: {entry.data_date}"
                )
        
        return lines