"""
Output Formatters

Format country data for different outputs.
"""

from .console_formatter import ConsoleFormatter
from .html_formatter import HTMLFormatter

__all__ = ["ConsoleFormatter", "HTMLFormatter"]