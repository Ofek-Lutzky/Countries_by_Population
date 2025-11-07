"""
Flag Service

Application service for coordinating flag downloads.
"""

import logging
from typing import Dict, List, Optional
from bs4 import BeautifulSoup

from ...domain.models.country import Country

logger = logging.getLogger(__name__)


class FlagService:
    """
    Service for managing flag image downloads.
    
    Orchestrates the flag downloading process and updates Country entities.
    
    Interview Note: This service demonstrates:
    - Service layer pattern (coordinates infrastructure)
    - Separation of concerns (download logic in infrastructure)
    - Data enrichment (adds flag_path to countries)
    """
    
    def __init__(self, flag_downloader):
        """
        Initialize flag service.
        
        Args:
            flag_downloader: Infrastructure component for downloading flags
        """
        self._downloader = flag_downloader
    
    async def download_and_attach_flags(
        self,
        countries: List[Country],
        table_html: BeautifulSoup
    ) -> List[Country]:
        """
        Download flags and create new Country instances with flag paths.
        
        Args:
            countries: List of Country entities (without flag paths)
            table_html: HTML table to extract flag URLs from
        
        Returns:
            New list of Country entities with flag_path populated
        
        Interview Note: Creates new Country instances rather than mutating
        existing ones (Countries are immutable/frozen dataclasses).
        """
        logger.info("Starting flag download process...")
        
        # Download flags
        flag_paths = await self._downloader.download_flags(countries, table_html)
        
        # Create new Country instances with flag paths
        countries_with_flags = []
        for country in countries:
            flag_path = flag_paths.get(country.name)
            
            # Create new Country instance with flag_path
            country_with_flag = Country(
                name=country.name,
                population=country.population,
                data_date=country.data_date,
                flag_path=flag_path
            )
            countries_with_flags.append(country_with_flag)
        
        # Log statistics
        with_flags = sum(1 for c in countries_with_flags if c.flag_path)
        logger.info(f"Attached flags to {with_flags}/{len(countries)} countries")
        
        return countries_with_flags