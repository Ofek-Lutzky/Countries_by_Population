"""
Application Interfaces

Defines abstractions that infrastructure layer must implement.
This enables dependency inversion - high-level code doesn't depend on low-level details.

Interview Note: These interfaces (Protocols) enable:
- Dependency injection
- Easy mocking for tests
- Swappable implementations
"""

from .http_client import IHTTPClient
from .html_parser import IHTMLParser

__all__ = ["IHTTPClient", "IHTMLParser"]