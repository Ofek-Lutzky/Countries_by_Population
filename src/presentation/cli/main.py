"""
Main CLI Entry Point

Command-line interface with dependency injection.
Provides a clean CLI for the Wikipedia Countries Population Scraper.

This is the "composition root" where all dependencies are wired together.
"""

import argparse
import asyncio
import logging
import sys

# Wikipedia URL
WIKIPEDIA_URL = "https://en.m.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """
    Parse command-line arguments.
    
    Configures command-line arguments for all application features.
    """
    parser = argparse.ArgumentParser(
        description='Scrape country population data from Wikipedia',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (console output)
  python -m src.presentation.cli.main

  # Generate HTML report
  python -m src.presentation.cli.main --html-report output.html

  # Download flags and generate HTML
  python -m src.presentation.cli.main --download-flags --html-report output.html

  # Filter by minimum population
  python -m src.presentation.cli.main --min-pop 100000000

  # Combine all options
  python -m src.presentation.cli.main --download-flags --html-report report.html --min-pop 50000000
        """
    )
    
    parser.add_argument(
        '--html-report',
        type=str,
        help='Generate HTML report at specified path'
    )
    
    parser.add_argument(
        '--download-flags',
        action='store_true',
        help='Download country flag images (async)'
    )
    
    parser.add_argument(
        '--flags-dir',
        type=str,
        default='flags',
        help='Directory for flag images (default: flags/)'
    )
    
    parser.add_argument(
        '--min-population', '--min-pop',
        type=int,
        help='Filter countries by minimum population'
    )
    
    parser.add_argument(
        '--url',
        type=str,
        default=WIKIPEDIA_URL,
        help='Wikipedia URL to scrape (default: countries by population)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    return parser.parse_args()


async def run_scraper(args):
    """
    Main workflow - scrape, process, and output data.
    Main application workflow with proper dependency injection.

    
    This is where Clean Architecture shines:
    - All dependencies injected at composition root
    - Services coordinate workflows
    - Easy to test by injecting mocks
    - Easy to extend by swapping implementations
    """
    # Import here to avoid circular imports
    from ...application.services.scraper_service import ScraperService
    from ...application.services.data_service import DataService
    from ...application.services.flag_service import FlagService
    from ...infrastructure.http.requests_client import RequestsHTTPClient
    from ...infrastructure.parsing.beautifulsoup_parser import BeautifulSoupParser
    from ...infrastructure.async_io.flag_downloader import FlagDownloader
    from ..formatters.console_formatter import ConsoleFormatter
    from ..formatters.html_formatter import HTMLFormatter
    
    try:
        # === COMPOSITION ROOT: Wire up dependencies ===
        # This is the only place where we create concrete implementations
        
        logger.info("Initializing services...")
        
        # Infrastructure layer
        http_client = RequestsHTTPClient(max_retries=3, timeout=10)
        html_parser = BeautifulSoupParser()
        
        # Optional: Flag downloader (only if requested)
        flag_service = None
        if args.download_flags:
            flag_downloader = FlagDownloader(output_dir=args.flags_dir)
            flag_service = FlagService(flag_downloader)
            logger.info(f"Flag downloads enabled (output: {args.flags_dir}/)")
        
        # Application layer
        scraper_service = ScraperService(http_client, html_parser, flag_service)
        data_service = DataService()
        
        # Presentation layer
        console_formatter = ConsoleFormatter()
        html_formatter = HTMLFormatter()
        
        # === WORKFLOW EXECUTION ===
        
        # Step 1: Scrape data (with optional flag downloads)
        logger.info(f"Scraping data from {args.url}")
        countries = await scraper_service.scrape_countries(
            args.url,
            download_flags=args.download_flags
        )
        logger.info(f"Scraped {len(countries)} countries")
        
        if args.download_flags:
            with_flags = sum(1 for c in countries if c.flag_path)
            logger.info(f"Downloaded flags: {with_flags}/{len(countries)}")
        
        # Step 2: Process data
        if args.min_population:
            logger.info(f"Filtering by minimum population: {args.min_population:,}")
            countries = data_service.filter_by_min_population(countries, args.min_population)
            logger.info(f"After filtering: {len(countries)} countries")
        
        # Sort by population (descending)
        sorted_countries = data_service.sort_by_population(countries, descending=True)
        
        # Find duplicates
        duplicates = data_service.find_duplicates(countries)
        
        # Get statistics
        stats = data_service.get_statistics(sorted_countries)
        logger.info(f"Statistics: {stats}")
        
        # Step 3: Output results
        
        # Console output (always shown)
        console_output = console_formatter.format(sorted_countries, duplicates)
        print(console_output)
        
        # HTML report (if requested)
        if args.html_report:
            logger.info(f"Generating HTML report: {args.html_report}")
            html_formatter.write_to_file(sorted_countries, args.html_report, duplicates, stats)
            print(f"\n✅ HTML report written to: {args.html_report}")
            print(f"📊 Report includes statistics dashboard with {stats['total_countries']} countries")
        
        logger.info("Scraping completed successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"Error during scraping: {e}", exc_info=True)
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1


def main():
    """
    Main entry point.
    Application entry point with Clean Architecture dependency injection.

    
    Interview Note: This is the composition root where:
    - Dependencies are wired together
    - Async workflow is initiated
    - Exit codes are handled
    """
    args = parse_arguments()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run async workflow
    exit_code = asyncio.run(run_scraper(args))
    sys.exit(exit_code)


if __name__ == '__main__':
    main()