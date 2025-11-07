"""
HTTP Client Interface

Defines contract for HTTP operations.
Infrastructure layer provides concrete implementations.

Interview Note: Using Protocol (structural subtyping) instead of ABC
allows any class with matching methods to satisfy the interface without
explicit inheritance.
"""

from typing import Protocol


class IHTTPClient(Protocol):
    """
    Interface for HTTP client implementations.
    
    This abstraction enables:
    - Dependency injection in services
    - Easy mocking for tests
    - Swapping implementations (requests, aiohttp, httpx, etc.)
    
    Design Benefits:
    - Enables dependency injection and testability
    - Allows swapping HTTP libraries without changing business logic
    - Supports mocking for unit tests
    
    Interview Note: This demonstrates Dependency Inversion Principle -
    high-level ScraperService depends on this abstraction, not on
    concrete HTTP library.
    """
    
    async def fetch(self, url: str) -> str:
        """
        Fetch HTML content from URL.
        
        Args:
            url: URL to fetch
        
        Returns:
            HTML content as string
        
        Raises:
            Exception: If fetch fails after retries
        
        Interview Note: Async signature allows efficient I/O operations.
        All implementations must support async/await pattern.
        """
        ...