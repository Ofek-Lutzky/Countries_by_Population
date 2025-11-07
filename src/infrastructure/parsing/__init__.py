"""
HTML Parsing Infrastructure

Concrete implementations of HTML parser interface.
"""

from .beautifulsoup_parser import BeautifulSoupParser

__all__ = ["BeautifulSoupParser"]