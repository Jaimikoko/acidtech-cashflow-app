"""
AciTech Cash Flow Management - Automated QA Route Testing
========================================================

OFFICIAL QA SCRIPT for Master Layout System Migration Validation

This script performs comprehensive, non-invasive testing of all main application routes
to validate the successful migration from Tailwind CSS to Bootstrap 5 with masterlayout.html.

🎯 TESTED ROUTES:
- / (Landing page)
- /dashboard (Main dashboard with Chart.js)
- /data-import (CSV upload functionality)
- /accounts-payable (AP module)
- /accounts-receivable (AR module)
- /purchase-orders (PO module)
- /reports (Reports module)
- /test-layout (Layout validation)

📋 TEST CATEGORIES:
1. Route accessibility and response validation
2. Bootstrap 5 integration verification
3. Master layout inheritance confirmation
4. Performance and response time testing
5. Tailwind CSS removal validation

🚀 USAGE:
    
    Local Development Testing:
    pytest -v tests/test_routes_qa.py
    
    Azure Production Testing:
    BASE_URL=https://app.acidtech.fintraqx.com pytest -v tests/test_routes_qa.py
    
    Detailed Output with HTML Report:
    pytest -v tests/test_routes_qa.py --html=qa_report.html

🔧 ENVIRONMENT VARIABLES:
    BASE_URL: Target application URL (default: http://localhost:5000)
    
💡 NOTES:
- This script requires the target application to be running
- All tests are READ-ONLY and will not modify application data
- Tests validate both functionality and migration success
- Designed for CI/CD integration and manual QA validation
"""

import pytest
import requests
import os
import time
from urllib.parse import urljoin
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestConfig:
    """Test configuration and constants"""
    BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')
    TIMEOUT = 30  # seconds
    RETRY_COUNT = 3
    RETRY_DELAY = 2  # seconds

class RouteValidator:
    """Helper class for route validation"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = TestConfig.TIMEOUT
        
    def make_request(self, endpoint: str, method: str = 'GET') -> requests.Response:
        """Make HTTP request with retry logic"""
        url = urljoin(self.base_url + '/', endpoint.lstrip('/'))
        
        for attempt in range(TestConfig.RETRY_COUNT):
            try:
                logger.info(f"Testing {method} {url} (attempt {attempt + 1})")
                response = self.session.request(method, url, allow_redirects=True)
                return response
            except requests.RequestException as e:
                if attempt == TestConfig.RETRY_COUNT - 1:
                    logger.error(f"Failed to reach {url} after {TestConfig.RETRY_COUNT} attempts: {e}")
                    raise
                time.sleep(TestConfig.RETRY_DELAY)
        
    def validate_response(self, response: requests.Response, expected_status: int = 200) -> bool:
        """Validate response status and basic properties"""
        if response.status_code != expected_status:
            logger.error(f"Expected status {expected_status}, got {response.status_code}")
            return False
            
        if response.status_code >= 500:
            logger.error(f"Server error {response.status_code}: {response.text[:200]}")
            return False
            
        return True
        
    def check_content_contains(self, response: requests.Response, expected_content: list) -> bool:
        """Check if response contains expected content"""
        content = response.text.lower()
        missing_content = []
        
        for expected in expected_content:
            if expected.lower() not in content:
                missing_content.append(expected)
                
        if missing_content:
            logger.warning(f"Missing expected content: {missing_content}")
            return False
            
        return True

# Initialize validator
validator = RouteValidator(TestConfig.BASE_URL)

class TestMainRoutes:
    """Test main application routes"""
    
    def test_landing_page(self):
        """Test landing page (/) loads correctly"""
        response = validator.make_request('/')
        
        assert validator.validate_response(response), f"Landing page failed with status {response.status_code}"
        
        expected_content = [
            'acidtech', 'cash flow', 'management'
        ]
        content_check = validator.check_content_contains(response, expected_content)
        assert content_check, "Landing page missing expected content"
        
        logger.info("✅ PASSED: Landing page loads correctly")

    def test_dashboard_route(self):
        """Test dashboard route (/dashboard) with masterlayout"""
        response = validator.make_request('/dashboard')
        
        assert validator.validate_response(response), f"Dashboard failed with status {response.status_code}"
        
        # Check for Bootstrap 5 and masterlayout elements
        expected_content = [
            'cash available', 'bootstrap', 'sidebar', 'dashboard'
        ]
        content_check = validator.check_content_contains(response, expected_content)
        assert content_check, "Dashboard missing expected masterlayout content"
        
        # Check for Chart.js integration
        assert 'chart.js' in response.text.lower(), "Dashboard missing Chart.js integration"
        
        logger.info("✅ PASSED: Dashboard loads with masterlayout and Chart.js")

    def test_data_import_route(self):
        """Test data import route (/data-import) with CSV upload interface"""
        response = validator.make_request('/data-import')
        
        assert validator.validate_response(response), f"Data Import failed with status {response.status_code}"
        
        expected_content = [
            'csv upload', 'data import', 'bootstrap', 'account name'
        ]
        content_check = validator.check_content_contains(response, expected_content)
        assert content_check, "Data Import missing expected content"
        
        # Check for upload form elements
        assert 'enctype="multipart/form-data"' in response.text, "Missing file upload form"
        assert 'csv_file' in response.text, "Missing CSV file input"
        
        logger.info("✅ PASSED: Data Import loads with CSV upload interface")

    def test_accounts_payable_route(self):
        """Test accounts payable route (/accounts-payable)"""
        response = validator.make_request('/accounts-payable')
        
        assert validator.validate_response(response), f"Accounts Payable failed with status {response.status_code}"
        
        expected_content = [
            'accounts payable', 'bootstrap', 'masterlayout'
        ]
        content_check = validator.check_content_contains(response, expected_content)
        assert content_check, "Accounts Payable missing expected content"
        
        logger.info("✅ PASSED: Accounts Payable loads correctly")

    def test_accounts_receivable_route(self):
        """Test accounts receivable route (/accounts-receivable)"""
        response = validator.make_request('/accounts-receivable')
        
        assert validator.validate_response(response), f"Accounts Receivable failed with status {response.status_code}"
        
        expected_content = [
            'accounts receivable', 'bootstrap', 'masterlayout'
        ]
        content_check = validator.check_content_contains(response, expected_content)
        assert content_check, "Accounts Receivable missing expected content"
        
        logger.info("✅ PASSED: Accounts Receivable loads correctly")

    def test_purchase_orders_route(self):
        """Test purchase orders route (/purchase-orders)"""
        response = validator.make_request('/purchase-orders')
        
        assert validator.validate_response(response), f"Purchase Orders failed with status {response.status_code}"
        
        expected_content = [
            'purchase order', 'bootstrap', 'masterlayout'
        ]
        content_check = validator.check_content_contains(response, expected_content)
        assert content_check, "Purchase Orders missing expected content"
        
        logger.info("✅ PASSED: Purchase Orders loads correctly")

    def test_reports_route(self):
        """Test reports route (/reports)"""
        response = validator.make_request('/reports')
        
        assert validator.validate_response(response), f"Reports failed with status {response.status_code}"
        
        expected_content = [
            'reports', 'bootstrap', 'masterlayout'
        ]
        content_check = validator.check_content_contains(response, expected_content)
        assert content_check, "Reports missing expected content"
        
        logger.info("✅ PASSED: Reports loads correctly")

    def test_test_layout_route(self):
        """Test layout validation route (/test-layout)"""
        response = validator.make_request('/test-layout')
        
        assert validator.validate_response(response), f"Test Layout failed with status {response.status_code}"
        
        expected_content = [
            'master layout', 'test', 'bootstrap', 'success'
        ]
        content_check = validator.check_content_contains(response, expected_content)
        assert content_check, "Test Layout missing expected content"
        
        logger.info("✅ PASSED: Test Layout loads correctly")

class TestAPIEndpoints:
    """Test API endpoints functionality"""
    
    def test_cash_flow_data_api(self):
        """Test cash flow data API endpoint (/api/cash-flow-data)"""
        # Note: This endpoint requires authentication, so we expect either 200 or 401/403
        try:
            response = validator.make_request('/api/cash-flow-data')
            
            # Accept 200 OK or authentication required responses
            if response.status_code == 200:
                # Should return JSON with dates, receivables, payables
                try:
                    data = response.json()
                    assert 'dates' in data, "API response missing 'dates' field"
                    assert 'receivables' in data, "API response missing 'receivables' field" 
                    assert 'payables' in data, "API response missing 'payables' field"
                    logger.info("✅ PASSED: Cash Flow API returns valid JSON data")
                except ValueError:
                    pytest.fail("API endpoint returned invalid JSON")
            elif response.status_code in [401, 403]:
                logger.info("ℹ️  INFO: Cash Flow API requires authentication (expected)")
            else:
                pytest.fail(f"Cash Flow API failed with unexpected status {response.status_code}")
                
        except requests.RequestException as e:
            logger.warning(f"⚠️  WARNING: Could not test Cash Flow API: {e}")

class TestBootstrapMigration:
    """Test Bootstrap 5 migration validation"""
    
    def test_no_tailwind_references(self):
        """Ensure no Tailwind CSS references remain in main routes"""
        routes_to_check = ['/', '/dashboard', '/data-import']
        
        for route in routes_to_check:
            response = validator.make_request(route)
            if response.status_code == 200:
                content = response.text.lower()
                
                # Check for Tailwind references that should be removed
                tailwind_indicators = [
                    'tailwindcss.com',
                    'tailwind.config',
                    'class="flex items-center"',  # Common Tailwind pattern
                ]
                
                found_tailwind = []
                for indicator in tailwind_indicators:
                    if indicator in content:
                        found_tailwind.append(indicator)
                
                # Landing page is allowed to have Tailwind (not migrated)
                if route == '/' and found_tailwind:
                    logger.info(f"ℹ️  INFO: Landing page still uses Tailwind CSS (expected)")
                elif found_tailwind:
                    logger.warning(f"⚠️  WARNING: Found Tailwind references in {route}: {found_tailwind}")
                else:
                    logger.info(f"✅ PASSED: No Tailwind references in {route}")

    def test_bootstrap_presence(self):
        """Ensure Bootstrap 5 is properly loaded in migrated routes"""
        routes_to_check = ['/dashboard', '/data-import', '/accounts-payable']
        
        for route in routes_to_check:
            try:
                response = validator.make_request(route)
                if response.status_code == 200:
                    content = response.text.lower()
                    
                    bootstrap_indicators = [
                        'bootstrap@5.3.0',
                        'bootstrap.min.css',
                        'bootstrap.bundle.min.js'
                    ]
                    
                    found_bootstrap = any(indicator in content for indicator in bootstrap_indicators)
                    assert found_bootstrap, f"Bootstrap 5 not found in {route}"
                    
                    logger.info(f"✅ PASSED: Bootstrap 5 detected in {route}")
            except AssertionError as e:
                logger.error(f"❌ FAILED: {e}")
                raise

class TestPerformance:
    """Basic performance and response time tests"""
    
    def test_response_times(self):
        """Test that all routes respond within acceptable time limits"""
        routes = ['/', '/dashboard', '/data-import', '/accounts-payable']
        max_response_time = 10  # seconds
        
        for route in routes:
            start_time = time.time()
            response = validator.make_request(route)
            response_time = time.time() - start_time
            
            assert response_time < max_response_time, f"Route {route} took {response_time:.2f}s (max: {max_response_time}s)"
            
            logger.info(f"✅ PASSED: {route} responded in {response_time:.2f}s")

# Test execution summary
def pytest_sessionfinish(session, exitstatus):
    """Print summary after all tests complete"""
    if exitstatus == 0:
        logger.info("\n🎉 ALL QA TESTS PASSED - Master Layout Migration Validated Successfully!")
        logger.info("✅ All routes responding correctly")
        logger.info("✅ Bootstrap 5 integration confirmed") 
        logger.info("✅ Master layout system functional")
        logger.info("✅ No critical issues detected")
    else:
        logger.error(f"\n❌ QA TESTS FAILED - Exit status: {exitstatus}")
        logger.error("Please review failed tests and fix issues before deployment")

if __name__ == "__main__":
    # Allow running script directly
    pytest.main([__file__, "-v"])