"""
HTTP Infrastructure

Concrete implementations of HTTP client interface.
"""

from .requests_client import RequestsHTTPClient

__all__ = ["RequestsHTTPClient"]