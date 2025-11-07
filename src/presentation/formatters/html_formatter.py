"""
HTML Formatter

Generates HTML reports from country data with interactive filtering.
Creates responsive HTML tables with modern styling and client-side features.
"""

from typing import List, Dict
from datetime import datetime

from ...domain.models.country import Country


class HTMLFormatter:
    """
    Format country data as HTML report with interactive client-side filtering.
    
    Features:
    - Responsive HTML tables with modern styling
    - Interactive client-side filtering and sorting
    - Statistics dashboard with key metrics
    - Flag image display when available
    """
    
    def format(
        self,
        countries: List[Country],
        duplicates: Dict[str, List[Country]] = None,
        statistics: Dict[str, any] = None
    ) -> str:
        """
        Generate HTML report from country data.
        
        Args:
            countries: Sorted list of countries
            duplicates: Optional map of duplicate entries
            statistics: Optional statistics from DataService.get_statistics()
        
        Returns:
            Complete HTML document as string with interactive filtering
        """
        duplicates = duplicates or {}
        statistics = statistics or {}
        
        html_parts = []
        html_parts.append(self._generate_header())
        html_parts.append(self._generate_statistics_cards(statistics))
        html_parts.append(self._generate_filters(len(countries)))
        html_parts.append(self._generate_table(countries, duplicates))
        html_parts.append(self._generate_javascript())
        html_parts.append(self._generate_footer(len(countries)))
        
        return "\n".join(html_parts)
    
    def _generate_header(self) -> str:
        """Generate HTML header with CSS."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Countries by Population</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background-color: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.8em;
            font-weight: 300;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(240, 147, 251, 0.3);
            transition: transform 0.3s ease;
        }
        .stat-card:hover {
            transform: translateY(-5px);
        }
        .stat-card.primary {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3);
        }
        .stat-card.success {
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            box-shadow: 0 4px 15px rgba(67, 233, 123, 0.3);
        }
        .stat-card.warning {
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            box-shadow: 0 4px 15px rgba(250, 112, 154, 0.3);
        }
        .stat-value {
            font-size: 2.2em;
            font-weight: bold;
            margin-bottom: 5px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }
        .stat-label {
            font-size: 0.9em;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 500;
        }
        .stat-sublabel {
            font-size: 0.8em;
            opacity: 0.8;
            margin-top: 5px;
            font-style: italic;
        }
        .filters {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .filter-row {
            display: flex;
            gap: 25px;
            flex-wrap: wrap;
            align-items: flex-end;
        }
        .filter-group {
            flex: 1;
            min-width: 220px;
            margin-right: 10px;
        }
        .filter-group:last-child {
            margin-right: 0;
            margin-left: 15px;
        }
        .filter-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: white;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .filter-group input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 8px;
            font-size: 15px;
            background-color: rgba(255,255,255,0.95);
            transition: all 0.3s ease;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .filter-group input:focus {
            outline: none;
            border-color: #4CAF50;
            background-color: white;
            box-shadow: 0 4px 10px rgba(76, 175, 80, 0.3);
            transform: translateY(-2px);
        }
        .filter-group input::placeholder {
            color: #999;
            font-style: italic;
        }
        .reset-btn {
            padding: 12px 24px;
            background: linear-gradient(135deg, #f44336 0%, #e91e63 100%);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 15px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 10px rgba(244, 67, 54, 0.3);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .reset-btn:hover {
            background: linear-gradient(135deg, #d32f2f 0%, #c2185b 100%);
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(244, 67, 54, 0.4);
        }
        .reset-btn:active {
            transform: translateY(0);
        }
        .stats {
            margin-top: 15px;
            padding: 12px 20px;
            background-color: rgba(255,255,255,0.95);
            border-radius: 8px;
            font-size: 15px;
            font-weight: 600;
            color: #333;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .stats #visible-count {
            color: #4CAF50;
            font-size: 18px;
            font-weight: bold;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background-color: white;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            border-radius: 12px;
            overflow: hidden;
        }
        th {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            padding: 15px 12px;
            text-align: left;
            position: sticky;
            top: 0;
            z-index: 10;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-size: 0.9em;
        }
        td {
            padding: 12px;
            border-bottom: 1px solid #eee;
        }
        tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        tr:hover {
            background-color: #e3f2fd;
            transform: scale(1.01);
            transition: all 0.2s ease;
        }
        .duplicate {
            background: linear-gradient(90deg, #fff3cd 0%, #ffeaa7 100%);
            border-left: 4px solid #f39c12;
        }
        .duplicate:hover {
            background: linear-gradient(90deg, #ffeaa7 0%, #fdcb6e 100%);
        }
        .rank {
            text-align: right;
            font-weight: bold;
        }
        .population {
            text-align: right;
        }
        .flag-cell {
            text-align: center;
            width: 60px;
        }
        .flag-img {
            max-width: 40px;
            max-height: 30px;
            border: 1px solid #ddd;
        }
        .no-flag {
            color: #999;
            font-size: 0.9em;
        }
        .hidden {
            display: none;
        }
        footer {
            text-align: center;
            margin-top: 20px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌍 Countries by Population</h1>
"""
    
    def _generate_statistics_cards(self, statistics: Dict[str, any]) -> str:
        """Generate statistics cards from DataService.get_statistics()."""
        if not statistics:
            return ""
        
        # Format numbers with commas
        def format_number(num):
            if isinstance(num, (int, float)):
                return f"{num:,.0f}" if isinstance(num, float) else f"{num:,}"
            return str(num)
        
        total_countries = statistics.get('total_countries', 0)
        total_population = statistics.get('total_population', 0)
        avg_population = statistics.get('average_population', 0)
        max_population = statistics.get('max_population', 0)
        min_population = statistics.get('min_population', 0)
        largest_country = statistics.get('largest_country', 'N/A')
        smallest_country = statistics.get('smallest_country', 'N/A')
        
        return f"""
    <!-- Statistics Cards -->
    <div class="stats-grid">
        <div class="stat-card primary">
            <div class="stat-value">{format_number(total_countries)}</div>
            <div class="stat-label">Total Countries</div>
        </div>
        <div class="stat-card success">
            <div class="stat-value">{format_number(total_population)}</div>
            <div class="stat-label">Total Population</div>
            <div class="stat-sublabel">All countries combined</div>
        </div>
        <div class="stat-card warning">
            <div class="stat-value">{format_number(avg_population)}</div>
            <div class="stat-label">Average Population</div>
            <div class="stat-sublabel">Per country</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{largest_country}</div>
            <div class="stat-label">Most Populous</div>
            <div class="stat-sublabel">{format_number(max_population)} people</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{smallest_country}</div>
            <div class="stat-label">Least Populous</div>
            <div class="stat-sublabel">{format_number(min_population)} people</div>
        </div>
    </div>
"""
    
    def _generate_filters(self, total_count: int) -> str:
        """Generate interactive filter controls."""
        return f"""
    <!-- Filter Controls -->
    <div class="filters">
        <div class="filter-row">
            <div class="filter-group">
                <label for="search-country">🔍 Search Country:</label>
                <input type="text" id="search-country" placeholder="Type to search countries...">
            </div>
            <div class="filter-group">
                <label for="min-population">👥 Min Population:</label>
                <input type="number" id="min-population" placeholder="e.g., 1000000" min="0">
            </div>
            <div class="filter-group">
                <label for="max-population">👥 Max Population:</label>
                <input type="number" id="max-population" placeholder="e.g., 100000000" min="0">
            </div>
            <div class="filter-group" style="display: flex; align-items: flex-end;">
                <button class="reset-btn" onclick="resetFilters()">Reset Filters</button>
            </div>
        </div>
        <div class="stats" id="filter-stats">
            Showing <span id="visible-count">{total_count}</span> of {total_count} countries
        </div>
    </div>
"""
    
    def _generate_table(
        self,
        countries: List[Country],
        duplicates: Dict[str, List[Country]]
    ) -> str:
        """Generate HTML table with country data."""
        lines = []
        lines.append('    <table id="countries-table">')
        lines.append('        <thead>')
        lines.append('            <tr>')
        lines.append('                <th>Rank</th>')
        lines.append('                <th>Flag</th>')
        lines.append('                <th>Country</th>')
        lines.append('                <th>Population</th>')
        lines.append('                <th>Date</th>')
        lines.append('            </tr>')
        lines.append('        </thead>')
        lines.append('        <tbody id="table-body">')
        
        for rank, country in enumerate(countries, 1):
            # Add duplicate class if country appears multiple times
            css_class = ' class="duplicate"' if country.name in duplicates else ''
            
            lines.append(f'            <tr{css_class} data-country="{country.name.lower()}" data-population="{country.population}">')
            lines.append(f'                <td class="rank">{rank}</td>')
            
            # Flag cell
            if country.flag_path:
                lines.append(f'                <td class="flag-cell">')
                lines.append(f'                    <img src="{country.flag_path}" alt="{country.name} flag" class="flag-img">')
                lines.append(f'                </td>')
            else:
                lines.append(f'                <td class="flag-cell"><span class="no-flag">—</span></td>')
            
            lines.append(f'                <td>{country.name}</td>')
            lines.append(f'                <td class="population">{country.format_population()}</td>')
            lines.append(f'                <td>{country.data_date}</td>')
            lines.append('            </tr>')
        
        lines.append('        </tbody>')
        lines.append('    </table>')
        
        return "\n".join(lines)
    
    def _generate_javascript(self) -> str:
        """Generate JavaScript for interactive filtering."""
        return """
    <script>
        // Get filter elements
        const searchInput = document.getElementById('search-country');
        const minPopInput = document.getElementById('min-population');
        const maxPopInput = document.getElementById('max-population');
        const tableBody = document.getElementById('table-body');
        const visibleCount = document.getElementById('visible-count');
        const totalCount = tableBody.querySelectorAll('tr').length;

        // Apply filters function
        function applyFilters() {
            const searchTerm = searchInput.value.toLowerCase().trim();
            const minPop = parseInt(minPopInput.value) || 0;
            const maxPop = parseInt(maxPopInput.value) || Infinity;

            const rows = tableBody.querySelectorAll('tr');
            let visibleRows = 0;

            rows.forEach(row => {
                const country = row.getAttribute('data-country');
                const population = parseInt(row.getAttribute('data-population'));

                // Check all filter conditions
                const matchesSearch = country.includes(searchTerm);
                const matchesMinPop = population >= minPop;
                const matchesMaxPop = population <= maxPop;

                // Show/hide row based on filters
                if (matchesSearch && matchesMinPop && matchesMaxPop) {
                    row.classList.remove('hidden');
                    visibleRows++;
                } else {
                    row.classList.add('hidden');
                }
            });

            // Update stats
            visibleCount.textContent = visibleRows;
        }

        // Reset filters function
        function resetFilters() {
            searchInput.value = '';
            minPopInput.value = '';
            maxPopInput.value = '';
            applyFilters();
        }

        // Add event listeners
        searchInput.addEventListener('input', applyFilters);
        minPopInput.addEventListener('input', applyFilters);
        maxPopInput.addEventListener('input', applyFilters);

        // Allow Enter key to trigger filter
        [searchInput, minPopInput, maxPopInput].forEach(input => {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    applyFilters();
                }
            });
        });
    </script>
"""
    
    def _generate_footer(self, total_count: int) -> str:
        """Generate HTML footer with metadata."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"""
        <footer>
            <p>Total countries: {total_count}</p>
            <p>Generated: {timestamp}</p>
            <p>Source: Wikipedia - List of countries by population</p>
            <p>🔧 Built with Clean Architecture (V3)</p>
        </footer>
    </div>
</body>
</html>
"""

    def write_to_file(
        self,
        countries: List[Country],
        output_path: str,
        duplicates: Dict[str, List[Country]] = None,
        statistics: Dict[str, any] = None
    ) -> None:
        """
        Generate HTML and write to file.
        
        Args:
            countries: Sorted list of countries
            output_path: Path to write HTML file
            duplicates: Optional map of duplicates
            statistics: Optional statistics from DataService.get_statistics()
        """
        html_content = self.format(countries, duplicates, statistics)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)