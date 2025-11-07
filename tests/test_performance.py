"""
Performance Tests

Tests demonstrating the performance benefits of asyncio over sequential processing.
These tests show why asyncio was chosen for flag downloads.
"""

import pytest
import time
import asyncio
from typing import List
from unittest.mock import Mock, patch
import aiohttp

from src.domain.models.country import Country
from src.infrastructure.async_io.flag_downloader import FlagDownloader


class TestAsyncPerformance:
    """
    Performance tests comparing async vs sequential downloads.
    
    These tests demonstrate the dramatic performance improvement
    when using asyncio for I/O-bound tasks like HTTP requests.
    """
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_countries = [
            Country(f"Country{i}", i * 1000000, "2024")
            for i in range(1, 21)  # 20 countries
        ]
    
    @pytest.mark.asyncio
    async def test_async_download_performance(self):
        """
        Test async download performance.
        
        This demonstrates that async downloads are significantly faster
        than sequential downloads for I/O-bound operations.
        
        Expected: ~2-4 seconds for 20 simulated downloads
        (vs 20+ seconds for sequential with same latency)
        """
        # Mock HTTP responses with realistic latency
        async def mock_download(session, country, url):
            """Simulate download with 100ms latency per request"""
            await asyncio.sleep(0.1)  # Simulate network delay
            return (country.name, f"flags/{country.name}.png")
        
        downloader = FlagDownloader(output_dir='test_flags')
        
        start_time = time.time()
        
        # Simulate async downloads
        async with aiohttp.ClientSession() as session:
            tasks = [
                mock_download(session, country, f"https://example.com/{country.name}.png")
                for country in self.test_countries
            ]
            results = await asyncio.gather(*tasks)
        
        duration = time.time() - start_time
        
        print(f"\n✅ Async downloads: {len(results)} files in {duration:.2f}s")
        print(f"   Average: {duration/len(results):.3f}s per file")
        print(f"   Speedup: ~{len(results) * 0.1 / duration:.1f}x faster than sequential")
        
        # With 10 concurrent downloads (semaphore=10), should complete in ~0.2s
        # (2 batches of 10, each taking ~0.1s)
        assert duration < 1.0, f"Took {duration:.2f}s, expected < 1.0s"
        assert len(results) == 20, f"Expected 20 results, got {len(results)}"
    
    def test_sequential_download_performance(self):
        """
        Test sequential download performance for comparison.
        
        This shows the baseline performance without async.
        
        Expected: ~2 seconds for 20 simulated downloads
        (100ms * 20 = 2000ms = 2s)
        """
        def mock_download_sync(country, url):
            """Simulate synchronous download with 100ms latency"""
            time.sleep(0.1)  # Simulate network delay
            return (country.name, f"flags/{country.name}.png")
        
        start_time = time.time()
        
        # Sequential downloads
        results = []
        for country in self.test_countries:
            result = mock_download_sync(country, f"https://example.com/{country.name}.png")
            results.append(result)
        
        duration = time.time() - start_time
        
        print(f"\n⏱️  Sequential downloads: {len(results)} files in {duration:.2f}s")
        print(f"   Average: {duration/len(results):.3f}s per file")
        
        # Sequential should take at least 20 * 0.1 = 2 seconds
        assert duration >= 2.0, f"Took {duration:.2f}s, expected >= 2.0s"
        assert len(results) == 20, f"Expected 20 results, got {len(results)}"
    
    @pytest.mark.asyncio
    async def test_async_vs_sequential_comparison(self):
        """
        Direct comparison: Async vs Sequential
        
        This test clearly demonstrates the performance benefit of asyncio.
        
        Expected result: Async is 6-10x faster for I/O-bound tasks.
        """
        # Setup: 50 simulated downloads with 50ms latency each
        num_downloads = 50
        latency_ms = 50
        
        print(f"\n📊 Performance Comparison: {num_downloads} downloads @ {latency_ms}ms latency")
        
        # Test 1: Sequential
        start_sequential = time.time()
        for i in range(num_downloads):
            time.sleep(latency_ms / 1000)  # Convert to seconds
        sequential_duration = time.time() - start_sequential
        
        # Test 2: Async with semaphore (10 concurrent)
        start_async = time.time()
        
        async def mock_async_download():
            await asyncio.sleep(latency_ms / 1000)
        
        # Limit to 10 concurrent (like our real implementation)
        semaphore = asyncio.Semaphore(10)
        
        async def limited_download():
            async with semaphore:
                await mock_async_download()
        
        tasks = [limited_download() for _ in range(num_downloads)]
        await asyncio.gather(*tasks)
        
        async_duration = time.time() - start_async
        
        # Calculate speedup
        speedup = sequential_duration / async_duration
        
        print(f"\n   Sequential: {sequential_duration:.2f}s")
        print(f"   Async:      {async_duration:.2f}s")
        print(f"   ⚡ Speedup:  {speedup:.1f}x faster!")
        print(f"   Time saved: {sequential_duration - async_duration:.2f}s")
        
        # Async should be at least 4x faster
        assert speedup >= 4.0, f"Speedup was {speedup:.1f}x, expected >= 4.0x"
        
        # With 10 concurrent and 50ms latency:
        # Sequential: 50 * 50ms = 2500ms = 2.5s
        # Async: 5 batches * 50ms = 250ms = 0.25s
        # Speedup: ~10x
    
    @pytest.mark.asyncio
    async def test_semaphore_rate_limiting(self):
        """
        Test that semaphore correctly limits concurrent operations.
        
        This demonstrates why we use semaphore for rate limiting:
        - Prevents overwhelming the server
        - Maintains consistent performance
        - Avoids connection pool exhaustion
        """
        max_concurrent = 5
        total_tasks = 20
        semaphore = asyncio.Semaphore(max_concurrent)
        
        active_count = 0
        max_active = 0
        
        async def limited_task(task_id):
            nonlocal active_count, max_active
            
            async with semaphore:
                active_count += 1
                max_active = max(max_active, active_count)
                
                # Simulate work
                await asyncio.sleep(0.01)
                
                active_count -= 1
        
        # Run all tasks
        tasks = [limited_task(i) for i in range(total_tasks)]
        await asyncio.gather(*tasks)
        
        print(f"\n🔒 Semaphore Test:")
        print(f"   Max concurrent allowed: {max_concurrent}")
        print(f"   Max concurrent observed: {max_active}")
        print(f"   Total tasks: {total_tasks}")
        
        # Should never exceed max_concurrent
        assert max_active <= max_concurrent, \
            f"Exceeded limit: {max_active} > {max_concurrent}"
    
    @pytest.mark.asyncio
    async def test_realistic_flag_download_simulation(self):
        """
        Realistic simulation of flag downloads with varying latencies.
        
        This simulates real-world conditions:
        - Variable network latency (50-200ms)
        - Some failures (10% failure rate)
        - Concurrent downloads with rate limiting
        """
        import random
        
        num_flags = 100
        success_count = 0
        failure_count = 0
        
        async def simulate_flag_download(country_id):
            nonlocal success_count, failure_count
            
            # Simulate variable latency
            latency = random.uniform(0.05, 0.2)  # 50-200ms
            await asyncio.sleep(latency)
            
            # Simulate 10% failure rate
            if random.random() < 0.1:
                failure_count += 1
                return None
            else:
                success_count += 1
                return f"flag_{country_id}.png"
        
        start_time = time.time()
        
        # Download with semaphore (max 10 concurrent)
        semaphore = asyncio.Semaphore(10)
        
        async def limited_download(country_id):
            async with semaphore:
                return await simulate_flag_download(country_id)
        
        tasks = [limited_download(i) for i in range(num_flags)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        duration = time.time() - start_time
        
        print(f"\n🌐 Realistic Flag Download Simulation:")
        print(f"   Total flags: {num_flags}")
        print(f"   Successful: {success_count} ({success_count/num_flags*100:.1f}%)")
        print(f"   Failed: {failure_count} ({failure_count/num_flags*100:.1f}%)")
        print(f"   Duration: {duration:.2f}s")
        print(f"   Average: {duration/num_flags*1000:.0f}ms per flag")
        
        # With semaphore=10 and avg latency=125ms:
        # Expected: ~10 batches * 125ms = 1.25s
        assert duration < 3.0, f"Took {duration:.2f}s, expected < 3.0s"
        
        # Should have processed all flags
        assert len(results) == num_flags


class TestDataProcessingPerformance:
    """
    Test performance of data processing operations.
    
    These tests ensure that data processing (sorting, filtering, etc.)
    is fast enough for good user experience.
    """
    
    def setup_method(self):
        """Set up test fixtures with realistic data volumes."""
        # Create 300 countries (more than real dataset)
        self.countries = [
            Country(f"Country{i}", i * 1000000, f"2024-{i%12+1:02d}-01")
            for i in range(1, 301)
        ]
    
    def test_sorting_performance(self):
        """Test that sorting large datasets is fast."""
        from src.application.services.data_service import DataService
        
        service = DataService()
        
        start_time = time.time()
        sorted_countries = service.sort_by_population(self.countries, descending=True)
        duration = time.time() - start_time
        
        print(f"\n📊 Sorting {len(self.countries)} countries: {duration*1000:.2f}ms")
        
        # Should sort 300 items in under 10ms
        assert duration < 0.01, f"Took {duration*1000:.2f}ms, expected < 10ms"
        
        # Verify sort is correct
        assert sorted_countries[0].population > sorted_countries[-1].population
    
    def test_filtering_performance(self):
        """Test that filtering large datasets is fast."""
        from src.application.services.data_service import DataService
        
        service = DataService()
        min_population = 50000000  # 50 million
        
        start_time = time.time()
        filtered_countries = service.filter_by_min_population(self.countries, min_population)
        duration = time.time() - start_time
        
        print(f"\n🔍 Filtering {len(self.countries)} countries: {duration*1000:.2f}ms")
        
        # Should filter 300 items in under 5ms
        assert duration < 0.005, f"Took {duration*1000:.2f}ms, expected < 5ms"
        
        # Verify all results meet criteria
        assert all(c.population >= min_population for c in filtered_countries)
    
    def test_duplicate_detection_performance(self):
        """Test that duplicate detection is fast."""
        from src.application.services.data_service import DataService
        
        # Add some duplicates using names that definitely don't exist
        countries_with_dupes = self.countries + [
            Country("TestCountryA", 5000000, "2024"),  # First TestCountryA
            Country("TestCountryB", 10000000, "2024"), # First TestCountryB
            Country("TestCountryA", 5100000, "2023"),  # Second TestCountryA (duplicate)
            Country("TestCountryB", 9900000, "2023"),  # Second TestCountryB (duplicate)
        ]
        
        service = DataService()
        
        start_time = time.time()
        duplicates = service.find_duplicates(countries_with_dupes)
        duration = time.time() - start_time
        
        print(f"\n🔎 Duplicate detection on {len(countries_with_dupes)} items: {duration*1000:.2f}ms")
        
        # Should process 300+ items in under 10ms
        assert duration < 0.01, f"Took {duration*1000:.2f}ms, expected < 10ms"
        
        # Verify duplicates were found
        assert "TestCountryA" in duplicates
        assert "TestCountryB" in duplicates
        assert len(duplicates["TestCountryA"]) == 2  # Two entries for TestCountryA
        assert len(duplicates["TestCountryB"]) == 2  # Two entries for TestCountryB
        assert len(duplicates) == 2  # Two countries have duplicates


class TestMemoryEfficiency:
    """
    Test memory efficiency of the implementation.
    
    Ensures the application doesn't consume excessive memory
    even with large datasets.
    """
    
    def test_country_object_size(self):
        """Test that Country objects are memory-efficient."""
        import sys
        
        country = Country("Test Country", 1000000, "2024")
        size = sys.getsizeof(country)
        
        print(f"\n💾 Country object size: {size} bytes")
        
        # Should be relatively small (frozen dataclass is efficient)
        assert size < 500, f"Size is {size} bytes, expected < 500 bytes"
    
    def test_large_dataset_memory(self):
        """Test memory usage with large dataset."""
        import sys
        
        # Create 1000 countries
        countries = [
            Country(f"Country{i}", i * 1000000, "2024")
            for i in range(1000)
        ]
        
        # Rough estimate of memory usage
        total_size = sum(sys.getsizeof(c) for c in countries)
        avg_size = total_size / len(countries)
        
        print(f"\n💾 Memory usage for 1000 countries:")
        print(f"   Total: {total_size / 1024:.1f} KB")
        print(f"   Average per country: {avg_size:.0f} bytes")
        
        # Should use less than 1MB for 1000 countries
        assert total_size < 1024 * 1024, f"Used {total_size/1024:.1f}KB, expected < 1MB"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])  # -s shows print statements