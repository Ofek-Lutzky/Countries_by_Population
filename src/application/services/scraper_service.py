"""
Scraper Service

Orchestrates the web scraping workflow.
Coordinates between HTTP client, parser, and domain validators.

This service coordinates the complete web scraping workflow.
Orchestrates HTTP fetching, HTML parsing, and data extraction.

Interview Note: This demonstrates Service Layer pattern - orchestrates
multiple components without containing business logic itself.
"""

from typing import List, Optional
import logging

from ...domain.models.country import Country
from ...domain.validators.data_validator import DataValidator
from ...domain.exceptions import InvalidCountryDataError
from ..interfaces.http_client import IHTTPClient
from ..interfaces.html_parser import IHTMLParser

logger = logging.getLogger(__name__)


class ScraperService:
    """
    Service for scraping country data from Wikipedia.
    
    Design Benefits:
    - Single responsibility: coordinates scraping workflow
    - Clean separation between HTTP, parsing, and data processing
    - Dependency injection enables testing and flexibility
    
    Interview Points:
    - Dependency Injection: Dependencies passed via constructor
    - Single Responsibility: Only coordinates, doesn't implement details
    - Testability: Easy to inject mocks for testing
    - Open/Closed: Can add new scraping sources without modifying this
    """
    
    def __init__(
        self,
        http_client: IHTTPClient,
        html_parser: IHTMLParser,
        flag_service: Optional['FlagService'] = None
    ):
        """
        Initialize scraper service with dependencies.
        
        Args:
            http_client: HTTP client for fetching pages
            html_parser: Parser for extracting data from HTML
            flag_service: Optional service for downloading flags
        
        Interview Note: Constructor injection is preferred over setter
        injection because it makes dependencies explicit and prevents
        invalid states (service without required dependencies).
        FlagService is optional to support running without flag downloads.
        """
        self._http = http_client
        self._parser = html_parser
        self._validator = DataValidator()
        self._flag_service = flag_service
    
    async def scrape_countries(
        self,
        url: str,
        download_flags: bool = False
    ) -> List[Country]:
        """
        Main use case: Scrape country population data from Wikipedia.
        
        Orchestrates the complete workflow:
        1. Fetch HTML (via IHTTPClient)
        2. Extract table (via IHTMLParser)
        3. Parse rows (via IHTMLParser)
        4. Validate and build entities (via DataValidator + Country)
        5. Optionally download flags (via FlagService)
        
        Workflow steps:
        1. Fetch HTML from Wikipedia
        2. Extract target table from HTML
        3. Parse rows into structured data
        4. Build Country domain objects
        - extract_target_table (lines 71-113) -> self._parser.extract_table()
        - parse_rows (lines 195-280) -> self._parser.parse_rows()
        - build_dataset (lines 283-342) -> self._build_countries()
        - download_flags_async (lines 484-582) -> self._flag_service
        
        Args:
            url: Wikipedia URL to scrape
            download_flags: Whether to download flag images
        
        Returns:
            List of Country domain entities
        
        Raises:
            Exception: If scraping fails (specific exceptions from dependencies)
        
        Interview Note: Async to allow efficient I/O operations.
        Each step can fail independently, with appropriate error handling.
        """
        try:
            logger.info(f"Starting scrape from {url}")
            
            # Step 1: Fetch HTML
            html = await self._http.fetch(url)
            logger.debug(f"Fetched {len(html)} bytes of HTML")
            
            # Step 2: Extract table
            table = self._parser.extract_table(html)
            logger.debug("Extracted population table")
            
            # Step 3: Parse rows
            raw_data = self._parser.parse_rows(table)
            logger.info(f"Parsed {len(raw_data)} raw data rows")
            
            # Step 4: Build domain entities
            countries = self._build_countries(raw_data)
            logger.info(f"Successfully built {len(countries)} Country entities")
            
            # Step 5: Optionally download flags
            if download_flags and self._flag_service:
                logger.info("Starting flag downloads...")
                countries = await self._flag_service.download_and_attach_flags(
                    countries, table
                )
            elif download_flags and not self._flag_service:
                logger.warning("Flag downloads requested but FlagService not available")
            
            return countries
            
        except Exception as e:
            logger.error(f"Scraping failed: {e}", exc_info=True)
            raise
    
    def _build_countries(self, raw_data: List[dict]) -> List[Country]:
        """
        Convert raw data dictionaries to domain entities.
        Builds Country domain objects from parsed row data.

        
        Handles:
        - Data validation via DataValidator
        - Entity creation with Country constructor
        - Graceful handling of invalid entries (log and skip)
        
        Args:
            raw_data: List of dictionaries with keys: name, population, date
        
        Returns:
            List of valid Country entities
        
        Interview Note: This shows graceful degradation - one bad entry
        doesn't stop processing. We log warnings but continue with valid data.
        """
        countries = []
        skipped_count = 0
        
        for idx, raw in enumerate(raw_data, 1):
            try:
                # Validate and clean raw data
                name, population, date = self._validator.validate_country_data(
                    raw['name'],
                    raw['population'],
                    raw['date']
                )
                
                # Create domain entity
                # Country constructor validates invariants
                country = Country(
                    name=name,
                    population=population,
                    data_date=date,
                    flag_path=None  # Set later by flag service if needed
                )
                
                countries.append(country)
                
            except (InvalidCountryDataError, KeyError, ValueError) as e:
                # Log but don't fail entire operation
                logger.warning(
                    f"Skipping invalid entry {idx}/{len(raw_data)}: {e}. "
                    f"Raw data: {raw}"
                )
                skipped_count += 1
                continue
        
        if skipped_count > 0:
            logger.info(f"Skipped {skipped_count} invalid entries")
        
        return countries