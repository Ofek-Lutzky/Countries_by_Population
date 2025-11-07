"""
BeautifulSoup HTML Parser

Concrete implementation of IHTMLParser using BeautifulSoup.
Handles HTML parsing and data extraction from Wikipedia tables.
"""

import logging
import re
from typing import List, Dict, Any

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class BeautifulSoupParser:
    """
    HTML parser implementation using BeautifulSoup4.
    
    Implementation features:
    - Robust table identification using multiple strategies
    - Flexible column mapping for different table structures
    - parse_rows (lines 195-280) -> parse_rows()
    
    Interview Note: BeautifulSoup chosen for:
    - Forgiving parser (handles malformed HTML)
    - Easy-to-use API
    - Good documentation
    - Wide adoption in Python community
    """
    
    def extract_table(self, html: str) -> Any:
        """
        Locate population table in Wikipedia HTML.
        Implementation details:
        - Uses multiple identification strategies for robustness
        - Validates table structure before processing

        
        Algorithm:
        1. Parse HTML with BeautifulSoup
        2. Find all tables with 'wikitable' class
        3. Check each table for expected headers (location/country + population)
        4. Return first matching table
        
        Args:
            html: Raw HTML content
        
        Returns:
            BeautifulSoup table object
        
        Raises:
            ValueError: If table cannot be found
        """
        soup = BeautifulSoup(html, 'html.parser')
        tables = soup.find_all('table', class_='wikitable')
        
        logger.info(f"Found {len(tables)} wikitable elements")
        
        for table in tables:
            if self._is_population_table(table):
                row_count = len(table.find_all('tr'))
                logger.info(f"Found target table with {row_count} rows")
                return table
        
        # Table not found
        raise ValueError(
            "Could not locate the population table. "
            "The Wikipedia page structure may have changed."
        )
    
    def _is_population_table(self, table: Any) -> bool:
        """
        Check if table is the population table.
        Validates table has expected column headers.

        
        Strategy: Look for header row containing both:
        - Location/country/area keyword
        - Population keyword
        """
        headers = table.find_all('th')
        header_texts = [th.get_text(strip=True).lower() for th in headers]
        
        # Check for location column
        has_location = any(
            keyword in h
            for h in header_texts
            for keyword in ['location', 'country', 'area']
        )
        
        # Check for population column
        has_population = any('population' in h for h in header_texts)
        
        return has_location and has_population
    
    def parse_rows(self, table: Any) -> List[Dict[str, str]]:
        """
        Extract raw data from table rows.
        
        Extracts structured data from table rows.
        Returns dictionaries for better data handling.
        
        Algorithm:
        1. Iterate through <tr> elements
        2. Skip header rows (containing <th>)
        3. Extract country name, population, date from cells
        4. Return raw strings (validation happens in domain layer)
        
        Args:
            table: BeautifulSoup table object
        
        Returns:
            List of dictionaries with keys: name, population, date
            All values are raw strings
        """
        rows = []
        table_rows = table.find_all('tr')
        
        logger.info(f"Processing {len(table_rows)} table rows")
        
        for row_idx, row in enumerate(table_rows):
            # Skip header rows
            if row.find('th'):
                continue
            
            cells = row.find_all('td')
            if len(cells) < 3:
                continue
            
            try:
                raw_data = self._extract_row_data(cells)
                if raw_data:
                    rows.append(raw_data)
            except Exception as e:
                logger.warning(f"Could not parse row {row_idx}: {e}")
                continue
        
        logger.info(f"Successfully extracted {len(rows)} data rows")
        return rows
    
    def _extract_row_data(self, cells: List[Any]) -> Dict[str, str]:
        """
        Extract country, population, and date from table cells.
        Implements flexible column mapping strategy.

        
        Column detection strategy:
        - Country: First substantial text cell (not a number)
        - Population: Large number with separators, no percentage
        - Date: After population, skip percentage column
        
        Returns:
            Dictionary with keys: name, population, date
            Or None if required data not found
        """
        # Find country name (first substantial text cell)
        country_name = None
        for cell in cells[:3]:
            text = cell.get_text(strip=True)
            if len(text) > 2 and not text.isdigit():
                country_name = text
                break
        
        if not country_name:
            return None
        
        # Find population (large number with separators)
        population_str = None
        pop_index = None
        for i, cell in enumerate(cells):
            text = cell.get_text(strip=True)
            # Population: contains digits with separators, not percentage
            if re.search(r'\d+[,\s]\d+', text) and '%' not in text:
                population_str = text
                pop_index = i
                break
        
        if not population_str:
            return None
        
        # Find date (after population, skip percentage column)
        date_str = "N/A"
        if pop_index is not None:
            for j in range(pop_index + 1, min(pop_index + 4, len(cells))):
                date_candidate = cells[j].get_text(strip=True)
                # Date should NOT be percentage, URL, or source reference
                if (date_candidate and
                    '%' not in date_candidate and
                    not date_candidate.startswith('http') and
                    '[' not in date_candidate and
                    len(date_candidate) > 0):
                    date_str = date_candidate
                    break
        
        return {
            'name': country_name,
            'population': population_str,
            'date': date_str
        }