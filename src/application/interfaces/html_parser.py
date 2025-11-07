"""
HTML Parser Interface

Defines contract for HTML parsing operations.
Infrastructure layer provides concrete implementations (e.g., BeautifulSoup).

Interview Note: Interface Segregation Principle - small, focused interface
that only includes parsing methods, nothing else.
"""

from typing import Protocol, List, Dict, Any


class IHTMLParser(Protocol):
    """
    Interface for HTML parsing implementations.
    
    This abstraction enables:
    - Using different parsing libraries (BeautifulSoup, lxml, html5lib)
    - Easy testing with mock parsers
    - Flexibility to add caching or preprocessing layers
    
    Design Benefits:
    - Abstracts HTML parsing implementation details
    - Enables dependency injection and testing
    - Allows swapping parsing libraries without changing business logic
    business logic.
    
    Interview Note: Parser returns dictionaries (data structures) rather
    than domain entities. This maintains separation - domain entity
    creation happens in application services, not infrastructure.
    """
    
    def extract_table(self, html: str) -> Any:
        """
        Locate and extract the population table from HTML.
        
        Args:
            html: Raw HTML content
        
        Returns:
            Table object (implementation-specific, e.g., BeautifulSoup Tag)
        
        Raises:
            Exception: If table cannot be found
        
        Interview Note: Returns 'Any' because different parsers have
        different table representations. The contract is that it returns
        something that parse_rows() can understand.
        """
        ...
    
    def parse_rows(self, table: Any) -> List[Dict[str, str]]:
        """
        Extract raw data from table rows.
        
        Args:
            table: Table object from extract_table()
        
        Returns:
            List of dictionaries with keys: name, population, date
            All values are raw strings (not cleaned or validated)
        
        Interview Note: Returns raw data (strings) rather than
        domain entities. Validation and entity creation happen
        in the service layer, maintaining separation of concerns.
        """
        ...