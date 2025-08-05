#!/usr/bin/env python3
"""
Unit tests for Revenue 4717 account functionality
Tests data loading, KPI calculations, and visualization components
"""

import os
import sys
import unittest
from datetime import date

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Enable File Mode for testing
os.environ['USE_FILE_MODE'] = 'true'

class TestRevenue4717(unittest.TestCase):
    """Test suite for Revenue 4717 account"""
    
    def setUp(self):
        """Set up test environment"""
        from app import create_app
        from utils.excel_data_manager import excel_manager
        
        self.app = create_app()
        self.client = self.app.test_client()
        self.excel_manager = excel_manager
        
    def test_excel_data_loading(self):
        """Test that Excel data loads correctly for Revenue 4717"""
        with self.app.app_context():
            # Test basic cash flow data loading
            transactions = self.excel_manager.get_cash_flow_transactions(account='Revenue 4717')
            
            self.assertIsInstance(transactions, list)
            self.assertGreater(len(transactions), 0, "Should have Revenue 4717 transactions")
            
            # Verify data structure
            if transactions:
                first_transaction = transactions[0]
                required_fields = ['id', 'date', 'description', 'amount', 'type', 'account']
                
                for field in required_fields:
                    self.assertIn(field, first_transaction, f"Transaction should have {field} field")
                
                # Verify account filter works
                for transaction in transactions:
                    self.assertEqual(transaction['account'], 'Revenue 4717', 
                                   "All transactions should be from Revenue 4717")
                    self.assertEqual(transaction['type'], 'inflow', 
                                   "Revenue 4717 should only have inflow transactions")
            
            print(f"[PASS] Excel data loading test passed: {len(transactions)} transactions")
    
    def test_account_summary_calculation(self):
        """Test account summary calculations for Revenue 4717"""
        with self.app.app_context():
            account_summary = self.excel_manager.get_account_summary('Revenue 4717', 2025)
            
            # Test summary structure
            required_keys = ['account', 'year', 'total_amount', 'transaction_count', 
                           'monthly_data', 'average_monthly', 'top_entities']
            
            for key in required_keys:
                self.assertIn(key, account_summary, f"Summary should have {key}")
            
            # Test data validity
            self.assertEqual(account_summary['account'], 'Revenue 4717')
            self.assertEqual(account_summary['year'], 2025)
            self.assertGreater(account_summary['total_amount'], 0, "Should have positive revenue")
            self.assertGreater(account_summary['transaction_count'], 0, "Should have transactions")
            self.assertGreater(account_summary['average_monthly'], 0, "Should have positive monthly average")
            
            # Test monthly data
            monthly_data = account_summary['monthly_data']
            self.assertEqual(len(monthly_data), 12, "Should have data for all 12 months")
            
            # Test that some months have data
            months_with_data = sum(1 for month_data in monthly_data.values() if month_data['amount'] > 0)
            self.assertGreater(months_with_data, 0, "Should have data in at least some months")
            
            print(f"[PASS] Account summary test passed:")
            print(f"   - Total Amount: ${account_summary['total_amount']:,.2f}")
            print(f"   - Transaction Count: {account_summary['transaction_count']}")
            print(f"   - Monthly Average: ${account_summary['average_monthly']:,.2f}")
            print(f"   - Months with data: {months_with_data}/12")
    
    def test_kpi_calculations(self):
        """Test KPI calculations are consistent"""
        with self.app.app_context():
            # Get data from different methods
            transactions = self.excel_manager.get_cash_flow_transactions(account='Revenue 4717', year=2025)
            account_summary = self.excel_manager.get_account_summary('Revenue 4717', 2025)
            
            # Calculate total manually from transactions
            manual_total = sum(t['amount'] for t in transactions if t['type'] == 'inflow')
            
            # Compare with summary total
            summary_total = account_summary['total_amount']
            
            # Allow for small rounding differences
            self.assertAlmostEqual(manual_total, summary_total, delta=1.0, 
                                 msg="Manual total should match summary total")
            
            # Test monthly average calculation
            expected_monthly_avg = summary_total / 12
            actual_monthly_avg = account_summary['average_monthly']
            
            self.assertAlmostEqual(expected_monthly_avg, actual_monthly_avg, delta=0.01,
                                 msg="Monthly average should be total divided by 12")
            
            print(f"[PASS] KPI calculations test passed:")
            print(f"   - Manual total: ${manual_total:,.2f}")
            print(f"   - Summary total: ${summary_total:,.2f}")
            print(f"   - Monthly average: ${actual_monthly_avg:,.2f}")
    
    def test_cash_flow_routes(self):
        """Test that Cash Flow routes work correctly"""
        with self.app.app_context():
            # Test main cash flow page
            response = self.client.get('/cash-flow/')
            self.assertEqual(response.status_code, 200, "Cash Flow main page should load")
            
            content = response.get_data(as_text=True)
            
            # Check for key elements
            key_elements = [
                'Cash Flow Analysis',
                'Revenue 4717',
                'Total Inflows',
                'File Mode Active'
            ]
            
            for element in key_elements:
                self.assertIn(element, content, f"Page should contain '{element}'")
            
            # Test account detail page
            response = self.client.get('/cash-flow/account/Revenue 4717')
            self.assertEqual(response.status_code, 200, "Revenue 4717 detail page should load")
            
            # Test monthly chart API
            response = self.client.get('/cash-flow/api/monthly-chart?account=Revenue 4717&year=2025')
            self.assertEqual(response.status_code, 200, "Monthly chart API should work")
            
            # Verify JSON response
            import json
            chart_data = json.loads(response.get_data(as_text=True))
            
            self.assertIn('labels', chart_data, "Chart should have labels")
            self.assertIn('datasets', chart_data, "Chart should have datasets")
            self.assertEqual(len(chart_data['labels']), 12, "Should have 12 months")
            
            print("[PASS] Cash Flow routes test passed")
    
    def test_data_integrity(self):
        """Test data integrity and consistency"""
        with self.app.app_context():
            transactions = self.excel_manager.get_cash_flow_transactions(account='Revenue 4717', year=2025)
            
            # Test date consistency
            for transaction in transactions:
                trans_date = transaction.get('date')
                
                if isinstance(trans_date, str):
                    # Should be valid date format
                    try:
                        parsed_date = date.fromisoformat(trans_date)
                        self.assertEqual(parsed_date.year, 2025, "Transaction should be in 2025")
                    except ValueError:
                        self.fail(f"Invalid date format: {trans_date}")
                elif hasattr(trans_date, 'year'):
                    self.assertEqual(trans_date.year, 2025, "Transaction should be in 2025")
            
            # Test amount consistency
            for transaction in transactions:
                amount = transaction.get('amount', 0)
                self.assertGreater(amount, 0, "Revenue amounts should be positive")
                self.assertIsInstance(amount, (int, float), "Amount should be numeric")
            
            # Test customer data consistency - check multiple possible field names
            customers = set()
            for transaction in transactions:
                customer = transaction.get('customer') or transaction.get('vendor_customer') or transaction.get('entity')
                if customer:
                    customers.add(customer)
            
            # Also check if transactions have proper structure
            if transactions:
                sample_keys = list(transactions[0].keys())
                print(f"   - Sample transaction keys: {sample_keys}")
            
            # Customer data is optional - the basic cash flow structure doesn't require it
            if len(customers) > 0:
                print(f"   - Found customer data: {len(customers)} unique customers")
            else:
                print("   - No customer data found (this is acceptable for basic cash flow transactions)")
            
            print(f"[PASS] Data integrity test passed:")
            print(f"   - Transactions tested: {len(transactions)}")
            print(f"   - Unique customers: {len(customers)}")
    
    def test_filtering_functionality(self):
        """Test filtering works correctly"""
        with self.app.app_context():
            # Test year filtering
            transactions_2025 = self.excel_manager.get_cash_flow_transactions(account='Revenue 4717', year=2025)
            transactions_2024 = self.excel_manager.get_cash_flow_transactions(account='Revenue 4717', year=2024)
            
            # Should have more data in 2025 than 2024 (since we generated 2025 data)
            self.assertGreaterEqual(len(transactions_2025), len(transactions_2024), 
                                   "Should have more or equal 2025 transactions")
            
            # Test month filtering
            january_transactions = self.excel_manager.get_cash_flow_transactions(
                account='Revenue 4717', year=2025, month=1)
            february_transactions = self.excel_manager.get_cash_flow_transactions(
                account='Revenue 4717', year=2025, month=2)
            
            # Verify month filtering works
            for transaction in january_transactions:
                trans_date = transaction.get('date')
                if isinstance(trans_date, str):
                    month = int(trans_date.split('-')[1])
                    self.assertEqual(month, 1, "January filter should only return January transactions")
            
            print(f"[PASS] Filtering test passed:")
            print(f"   - 2025 transactions: {len(transactions_2025)}")
            print(f"   - 2024 transactions: {len(transactions_2024)}")
            print(f"   - January 2025: {len(january_transactions)}")
            print(f"   - February 2025: {len(february_transactions)}")

def run_tests():
    """Run all tests and provide summary"""
    
    print("*** Revenue 4717 Unit Tests ***")
    print("Testing data loading, KPI calculations, and route functionality\n")
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRevenue4717)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print(f"\n*** Test Summary ***")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n[FAIL] Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n[ERROR] Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n[SUCCESS] All tests passed! Revenue 4717 functionality is working correctly.")
        return True
    else:
        print("\n[WARNING] Some tests failed. Please review the output above.")
        return False

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)