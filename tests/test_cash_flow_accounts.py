"""
Unit tests for Cash Flow Account Detail functionality
Tests all account types with enhanced filtering and visualization
"""

import unittest
import sys
import os
from datetime import datetime, date

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.routes.cash_flow.routes import ACCOUNT_MAPPINGS

class TestCashFlowAccounts(unittest.TestCase):
    """Test suite for all Cash Flow account details"""
    
    def setUp(self):
        """Set up test client and app context"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        """Clean up after tests"""
        self.app_context.pop()

    def test_account_mappings_exist(self):
        """Test that all required account mappings are configured"""
        required_accounts = ['Revenue 4717', 'Bill Pay 5285', 'Payroll 4079', 'Capital One']
        
        for account in required_accounts:
            self.assertIn(account, ACCOUNT_MAPPINGS, f"Account {account} should be in ACCOUNT_MAPPINGS")
            
            # Test account mapping structure
            mapping = ACCOUNT_MAPPINGS[account]
            self.assertIn('name', mapping, f"Account {account} should have 'name' field")
            self.assertIn('type', mapping, f"Account {account} should have 'type' field")
            self.assertIn('color', mapping, f"Account {account} should have 'color' field")
            
            # Validate color format (should be hex color)
            self.assertTrue(mapping['color'].startswith('#'), f"Account {account} color should be hex format")

    def test_all_account_detail_pages_load(self):
        """Test that detail page loads for each account"""
        for account_name in ACCOUNT_MAPPINGS.keys():
            with self.subTest(account=account_name):
                response = self.client.get(f'/cash-flow/account/{account_name}')
                self.assertEqual(response.status_code, 200, 
                               f"{account_name} detail page should load successfully")
                
                # Check that the page contains account-specific content
                response_text = response.get_data(as_text=True)
                self.assertIn('Account Detail', response_text, 
                            f"{account_name} should show 'Account Detail' title")
                self.assertIn(account_name, response_text, 
                            f"Page should contain account name {account_name}")

    def test_account_detail_with_filters(self):
        """Test account detail pages with various filters"""
        test_accounts = ['Revenue 4717', 'Bill Pay 5285']
        
        filter_combinations = [
            {'year': 2025},
            {'year': 2025, 'month': 1},
            {'year': 2024, 'month': 12},
            {'period': 'month'},
            {'period': 'year'},
        ]
        
        for account in test_accounts:
            for filters in filter_combinations:
                with self.subTest(account=account, filters=filters):
                    query_string = '&'.join([f'{k}={v}' for k, v in filters.items()])
                    response = self.client.get(f'/cash-flow/account/{account}?{query_string}')
                    
                    self.assertEqual(response.status_code, 200,
                                   f"{account} should load with filters: {filters}")

    def test_account_detail_contains_required_elements(self):
        """Test that account detail pages contain all required UI elements"""
        for account_name in ACCOUNT_MAPPINGS.keys():
            with self.subTest(account=account_name):
                response = self.client.get(f'/cash-flow/account/{account_name}')
                response_text = response.get_data(as_text=True)
                
                # Check for required sections
                required_elements = [
                    'Account Detail',  # Page title
                    'Total Amount',    # KPI card
                    'Monthly Average', # KPI card
                    'Peak Month',      # KPI card
                    'Growth Trend',    # KPI card
                    'Monthly Breakdown', # Chart section
                    'Recent Transactions', # Transaction table
                    'Back to Overview', # Navigation
                    'timePeriodFilter', # Filter controls
                    'monthFilter',
                    'yearFilter',
                ]
                
                for element in required_elements:
                    self.assertIn(element, response_text,
                                f"{account_name} page should contain '{element}'")

    def test_invalid_account_redirect(self):
        """Test that invalid account names redirect to main cash flow page"""
        invalid_accounts = ['NonExistentAccount', 'Random123', '']
        
        for invalid_account in invalid_accounts:
            with self.subTest(account=invalid_account):
                response = self.client.get(f'/cash-flow/account/{invalid_account}')
                # Should redirect (302) or not found (404)
                self.assertIn(response.status_code, [302, 404],
                            f"Invalid account {invalid_account} should redirect or return 404")

    def test_chart_data_structure(self):
        """Test that chart data is properly structured in account detail pages"""
        for account_name in ACCOUNT_MAPPINGS.keys():
            with self.subTest(account=account_name):
                response = self.client.get(f'/cash-flow/account/{account_name}')
                response_text = response.get_data(as_text=True)
                
                # Check for Chart.js elements
                chart_elements = [
                    'monthlyBreakdownChart',  # Chart canvas ID
                    'Chart.js',              # Chart library
                    'new Chart(',            # Chart initialization
                    'yAxisID',              # Dual Y-axis setup
                ]
                
                for element in chart_elements:
                    self.assertIn(element, response_text,
                                f"{account_name} should contain chart element: {element}")

    def test_responsive_ui_elements(self):
        """Test that responsive UI classes are present"""
        response = self.client.get('/cash-flow/account/Revenue 4717')
        response_text = response.get_data(as_text=True)
        
        essential_classes = [
            'col-lg-', 'col-md-',              # Essential Bootstrap responsive columns
            'card border-0 shadow-sm',         # Card styling
            'table-responsive',                # Responsive table
            'd-flex justify-content-between',  # Flex utilities
        ]
        
        for css_class in essential_classes:
            self.assertIn(css_class, response_text,
                        f"Should contain essential responsive CSS class: {css_class}")

    def test_filter_javascript_functions(self):
        """Test that filter JavaScript functions are present"""
        response = self.client.get('/cash-flow/account/Revenue 4717')
        response_text = response.get_data(as_text=True)
        
        js_functions = [
            'toggleCustomRange()',
            'applyFilters()',
            'resetFilters()',
            'showLoadingOverlay()',
        ]
        
        for function in js_functions:
            self.assertIn(function, response_text,
                        f"Should contain JavaScript function: {function}")

def run_tests():
    """Run all Cash Flow account tests"""
    print("*** Running Cash Flow Account Tests ***")
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCashFlowAccounts)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n*** Test Summary ***")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n[SUCCESS] All tests passed! Cash Flow module is working correctly.")
        return True
    else:
        print(f"\n[FAILED] {len(result.failures + result.errors)} tests failed.")
        return False

if __name__ == '__main__':
    run_tests()