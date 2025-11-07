"""
Test Suite for Wikipedia Countries Population Scraper

This package contains comprehensive unit tests, integration tests,
and performance tests.

Test modules:
- test_parsing.py: Data validation and parsing tests
- test_data_service.py: Business logic tests
- test_performance.py: Async performance and latency tests

Run all tests:
    pytest tests/ -v

Run with coverage:
    pytest tests/ --cov=src --cov-report=html

Run specific test file:
    pytest tests/test_parsing.py -v

Run performance tests:
    pytest tests/test_performance.py -v -s
"""