"""
Setup script for Wikipedia Countries Population Scraper.

This allows the package to be installed in development mode:
    pip install -e .

Which makes the 'src' module available for imports.
"""

from setuptools import setup, find_packages

setup(
    name="countries-population-scraper",
    version="1.0.0",
    description="Wikipedia Countries Population Scraper with Clean Architecture",
    author="Assignment Project",
    python_requires=">=3.8",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0", 
        "aiohttp>=3.9.0",
        "pytest>=7.4.0",
        "pytest-asyncio>=0.21.0",
        "pytest-cov>=4.1.0",
    ],
    entry_points={
        "console_scripts": [
            "countries-scraper=src.presentation.cli.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9", 
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)