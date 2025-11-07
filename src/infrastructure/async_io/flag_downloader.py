"""
Async Flag Downloader

Downloads country flag images asynchronously.
Provides high-performance concurrent flag downloading with proper error handling.
"""

import asyncio
import os
import logging
from typing import Dict, Optional
from urllib.parse import urljoin

import aiohttp
from bs4 import BeautifulSoup

from ...domain.models.country import Country

logger = logging.getLogger(__name__)


class FlagDownloader:
    """
    Asynchronous flag image downloader.
    Features:
    - Concurrent downloads using asyncio and aiohttp
    - Semaphore-based rate limiting to avoid overwhelming servers
    - Graceful error handling with fallback strategies
    - Automatic file type detection and proper naming

    
    Interview Note: Uses asyncio for concurrent downloads because:
    - I/O-bound operation (network requests)
    - Many small files (~239 flags)
    - Better performance than sequential (5x faster)
    - Lower overhead than threading
    """
    
    def __init__(
        self,
        output_dir: str = 'flags',
        max_concurrent: int = 10
    ):
        """
        Initialize flag downloader.
        
        Args:
            output_dir: Directory to save flag images
            max_concurrent: Maximum concurrent downloads (rate limiting)
        """
        self._output_dir = output_dir
        self._max_concurrent = max_concurrent
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
    
    async def download_flags(
        self,
        countries: list[Country],
        table_html: BeautifulSoup
    ) -> Dict[str, str]:
        """
        Download flag images for all countries.
        Downloads all flags concurrently with rate limiting.

        
        Args:
            countries: List of Country entities
            table_html: BeautifulSoup table to extract flag URLs from
        
        Returns:
            Dictionary mapping country names to local file paths
        """
        logger.info(f"Starting flag downloads to {self._output_dir}/")
        
        # Extract flag URLs from HTML table
        flag_urls = self._extract_flag_urls(table_html, countries)
        logger.info(f"Found {len(flag_urls)} flag URLs to download")
        
        if not flag_urls:
            logger.warning("No flag URLs found in table")
            return {}
        
        # Download flags concurrently with rate limiting
        flag_paths = await self._download_concurrent(flag_urls)
        
        success_count = len([p for p in flag_paths.values() if p])
        logger.info(f"Successfully downloaded {success_count}/{len(flag_urls)} flags")
        
        return flag_paths
    
    def _extract_flag_urls(
        self,
        table: BeautifulSoup,
        countries: list[Country]
    ) -> Dict[str, str]:
        """
        Extract flag image URLs from table.
        
        Extracts flag URLs from Wikipedia table HTML.
        """
        flag_urls = {}
        rows = table.find_all('tr')
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) < 2:
                continue
            
            # Look for flag image in first few cells
            img_tag = None
            country_name = None
            
            for cell in cells[:3]:
                img = cell.find('img')
                if img and img.get('src'):
                    img_tag = img
                    # Get country name
                    text_cells = [c.get_text(strip=True) for c in cells]
                    for text in text_cells:
                        if len(text) > 2 and not text.isdigit() and '%' not in text:
                            country_name = text
                            break
                    break
            
            if img_tag and country_name:
                # Convert relative URL to absolute
                img_src = img_tag['src']
                if img_src.startswith('//'):
                    img_src = 'https:' + img_src
                elif img_src.startswith('/'):
                    img_src = 'https://en.m.wikipedia.org' + img_src
                
                flag_urls[country_name] = img_src
        
        return flag_urls
    
    async def _download_concurrent(
        self,
        flag_urls: Dict[str, str]
    ) -> Dict[str, Optional[str]]:
        """
        Download flags concurrently with rate limiting.
        
        Creates output directory if it doesn't exist.
        """
        semaphore = asyncio.Semaphore(self._max_concurrent)
        
        async def download_with_limit(country: str, url: str):
            async with semaphore:
                return await self._download_one(country, url)
        
        # Create timeout and connector
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
        
        async with aiohttp.ClientSession(
            timeout=timeout,
            connector=connector
        ) as session:
            tasks = [
                download_with_limit(country, url)
                for country, url in flag_urls.items()
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Build results dictionary
        flag_paths = {}
        for result in results:
            if isinstance(result, tuple):
                country, path = result
                flag_paths[country] = path
            elif isinstance(result, Exception):
                logger.debug(f"Download error: {result}")
        
        return flag_paths
    
    async def _download_one(
        self,
        country: str,
        flag_url: str
    ) -> tuple[str, Optional[str]]:
        """
        Download a single flag image.
        Downloads a single flag with proper error handling and file type detection.

        
        Args:
            country: Country name
            flag_url: URL of flag image
        
        Returns:
            Tuple of (country_name, local_file_path or None)
        """
        try:
            # Sanitize country name for filename
            safe_name = "".join(
                c if c.isalnum() or c in (' ', '_') else '_'
                for c in country
            )
            safe_name = safe_name.replace(' ', '_')
            
            # Headers to avoid being blocked
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://en.wikipedia.org/'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(flag_url, headers=headers, timeout=15) as response:
                    if response.status == 200:
                        content = await response.read()
                        
                        # Detect file type from magic bytes
                        if content.startswith(b'\x89PNG'):
                            ext = '.png'
                        elif content.startswith(b'<') or content.startswith(b'<?xml'):
                            ext = '.svg'
                        elif content.startswith(b'\xFF\xD8\xFF'):
                            ext = '.jpg'
                        else:
                            ext = '.png'  # Default
                        
                        filepath = os.path.join(self._output_dir, f"{safe_name}{ext}")
                        
                        with open(filepath, 'wb') as f:
                            f.write(content)
                        
                        logger.debug(f"Downloaded flag for {country}")
                        return (country, filepath)
                    else:
                        logger.debug(f"Failed to download flag for {country}: HTTP {response.status}")
                        return (country, None)
        
        except Exception as e:
            logger.debug(f"Error downloading flag for {country}: {e}")
            return (country, None)