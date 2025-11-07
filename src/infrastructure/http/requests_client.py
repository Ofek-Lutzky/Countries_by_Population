"""
Requests HTTP Client

Concrete implementation of IHTTPClient using requests library.
Provides HTTP functionality with retry logic and proper error handling.
"""

import asyncio
import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)


class RequestsHTTPClient:
    """
    HTTP client implementation using requests library.
    
    Implementation Notes:
    - Class-based design enables configuration and dependency injection
    - Implements IHTTPClient interface
    - Async for consistency with other operations
    - Uses logger instead of print statements
    """
    
    DEFAULT_USER_AGENT = (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/91.0.4472.124 Safari/537.36'
    )
    
    def __init__(
        self,
        max_retries: int = 3,
        timeout: int = 10,
        user_agent: Optional[str] = None
    ):
        """
        Initialize HTTP client.
        
        Args:
            max_retries: Maximum retry attempts (default: 3)
            timeout: Request timeout in seconds (default: 10)
            user_agent: Custom user agent for web scraping
        """
        self._max_retries = max_retries
        self._timeout = timeout
        self._user_agent = user_agent or self.DEFAULT_USER_AGENT
        
        # Create session for connection reuse
        self._session = requests.Session()
        self._session.headers.update({'User-Agent': self._user_agent})
    
    async def fetch(self, url: str) -> str:
        """
        Fetch HTML content with retry logic and exponential backoff.
        Implementation details:
        - Uses exponential backoff for retries
        - Proper User-Agent header to avoid being blocked
        - Comprehensive error handling and logging

        
        Algorithm:
        1. Try to fetch (max_retries times)
        2. If fails, wait with exponential backoff (1s, 2s, 4s)
        3. Raise exception if all retries fail
        
        Args:
            url: URL to fetch
        
        Returns:
            HTML content as string
        
        Raises:
            requests.RequestException: If all retries fail
        """
        for attempt in range(self._max_retries):
            try:
                logger.info(
                    f"Fetching {url} (attempt {attempt + 1}/{self._max_retries})"
                )
                
                # Synchronous request (requests library is not async)
                # Wrapped in async function for interface compliance
                response = self._session.get(url, timeout=self._timeout)
                response.raise_for_status()
                
                logger.info(
                    f"Successfully fetched page ({len(response.text)} bytes)"
                )
                
                return response.text
                
            except requests.RequestException as e:
                if attempt < self._max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = 2 ** attempt
                    logger.warning(
                        f"Request failed: {e}. Retrying in {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(
                        f"Failed to fetch page after {self._max_retries} attempts"
                    )
                    raise
    
    def close(self):
        """Clean up session resources."""
        self._session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()