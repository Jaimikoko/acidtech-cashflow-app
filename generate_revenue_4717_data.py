#!/usr/bin/env python3
"""
Generate comprehensive 2025 Revenue 4717 dataset for Cash Flow analysis
Creates realistic monthly revenue patterns with seasonal variations
"""

import pandas as pd
import os
from datetime import datetime, date, timedelta
import random
import numpy as np

def generate_revenue_4717_dataset():
    """Generate comprehensive Revenue 4717 dataset for 2025"""
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join('static', 'uploads')
    os.makedirs(output_dir, exist_ok=True)
    
    # Base customers and their typical contract values
    customers = [
        {'name': 'Acme Corporation', 'monthly_base': 15000, 'contract_type': 'recurring', 'payment_terms': 'NET30'},
        {'name': 'Tech Solutions Inc', 'monthly_base': 12000, 'contract_type': 'recurring', 'payment_terms': 'NET15'},
        {'name': 'Global Systems Ltd', 'monthly_base': 18000, 'contract_type': 'project', 'payment_terms': 'NET45'},
        {'name': 'DataFlow Corp', 'monthly_base': 8500, 'contract_type': 'recurring', 'payment_terms': 'NET30'},
        {'name': 'CloudTech Partners', 'monthly_base': 10500, 'contract_type': 'project', 'payment_terms': 'NET30'},
        {'name': 'Digital Innovations', 'monthly_base': 14500, 'contract_type': 'recurring', 'payment_terms': 'NET30'},
        {'name': 'Enterprise Solutions', 'monthly_base': 22000, 'contract_type': 'project', 'payment_terms': 'NET60'},
        {'name': 'Smart Systems Co', 'monthly_base': 9500, 'contract_type': 'recurring', 'payment_terms': 'NET15'},
        {'name': 'Innovation Labs', 'monthly_base': 16000, 'contract_type': 'project', 'payment_terms': 'NET45'},
        {'name': 'Future Tech Inc', 'monthly_base': 11500, 'contract_type': 'recurring', 'payment_terms': 'NET30'}
    ]
    
    # Service types and their descriptions
    service_types = [
        'Software Development Services',
        'System Integration Project',
        'Consulting Services - Strategic Planning',
        'Cloud Migration Services',
        'Data Analytics Implementation',
        'Cybersecurity Assessment',
        'Digital Transformation Consulting',
        'API Development & Integration',
        'Infrastructure Optimization',
        'Business Process Automation'
    ]
    
    revenue_transactions = []
    transaction_id = 1
    
    # Generate data for each month of 2025
    for month in range(1, 13):
        # Seasonal multipliers (Q1 slower, Q2-Q3 peak, Q4 budget push)
        seasonal_multipliers = {
            1: 0.85, 2: 0.90, 3: 0.95,  # Q1 - slower start
            4: 1.05, 5: 1.10, 6: 1.15,  # Q2 - ramping up
            7: 1.10, 8: 1.05, 9: 1.20,  # Q3 - summer projects, Sept peak
            10: 1.15, 11: 1.25, 12: 1.30  # Q4 - budget flush, year-end push
        }
        
        month_multiplier = seasonal_multipliers[month]
        
        # Generate 2-4 transactions per customer per month
        for customer in customers:
            num_transactions = random.randint(2, 4)
            
            for _ in range(num_transactions):
                # Calculate amount with seasonal variation and randomness
                base_amount = customer['monthly_base'] / 3  # Divide by average transactions per month
                seasonal_amount = base_amount * month_multiplier
                # Add randomness (-20% to +30%)
                random_factor = random.uniform(0.8, 1.3)
                final_amount = seasonal_amount * random_factor
                
                # Round to nearest 100
                final_amount = round(final_amount / 100) * 100
                
                # Generate date within the month
                start_date = date(2025, month, 1)
                if month == 12:
                    end_date = date(2025, 12, 31)
                else:
                    end_date = date(2025, month + 1, 1) - timedelta(days=1)
                
                # Random date in month, with bias toward middle/end of month
                days_in_month = (end_date - start_date).days + 1
                # Weighted toward later in month (payment cycles)
                day_weights = list(range(1, days_in_month + 1))
                day_weights = [w * 1.5 if w > days_in_month * 0.5 else w for w in day_weights]
                selected_day = random.choices(range(days_in_month), weights=day_weights)[0]
                transaction_date = start_date + timedelta(days=selected_day)
                
                # Determine status based on date relative to today
                today = date.today()
                if transaction_date < today:
                    status = 'completed'
                elif transaction_date <= today + timedelta(days=30):
                    status = 'pending'
                else:
                    status = 'scheduled'
                
                # Generate realistic description
                service_type = random.choice(service_types)
                descriptions = [
                    f"{service_type} - {customer['name']}",
                    f"Monthly Service Fee - {customer['name']} ({service_type})",
                    f"Project Milestone Payment - {customer['name']}",
                    f"Contract Renewal - {customer['name']} ({service_type})",
                    f"Additional Services - {customer['name']}"
                ]
                description = random.choice(descriptions)
                
                revenue_transactions.append({
                    'id': transaction_id,
                    'date': transaction_date.strftime('%Y-%m-%d'),
                    'description': description,
                    'amount': final_amount,
                    'type': 'inflow',
                    'account': 'Revenue 4717',
                    'customer': customer['name'],
                    'status': status,
                    'payment_terms': customer['payment_terms'],
                    'contract_type': customer['contract_type'],
                    'month': month,
                    'quarter': f"Q{(month-1)//3 + 1}",
                    'service_category': service_type.split(' - ')[0] if ' - ' in service_type else service_type.split(' ')[0]
                })
                
                transaction_id += 1
    
    # Add some large project milestone payments
    milestone_payments = [
        {'customer': 'Enterprise Solutions', 'amount': 50000, 'month': 3, 'description': 'Major Implementation - Phase 1'},
        {'customer': 'Global Systems Ltd', 'amount': 35000, 'month': 6, 'description': 'System Overhaul - Completion Bonus'},
        {'customer': 'Innovation Labs', 'amount': 42000, 'month': 9, 'description': 'Digital Transformation - Final Delivery'},
        {'customer': 'Enterprise Solutions', 'amount': 60000, 'month': 12, 'description': 'Year-end Strategic Project Completion'}
    ]
    
    for milestone in milestone_payments:
        milestone_date = date(2025, milestone['month'], random.randint(15, 28))
        today = date.today()
        status = 'completed' if milestone_date < today else 'pending' if milestone_date <= today + timedelta(days=30) else 'scheduled'
        
        revenue_transactions.append({
            'id': transaction_id,
            'date': milestone_date.strftime('%Y-%m-%d'),
            'description': milestone['description'],
            'amount': milestone['amount'],
            'type': 'inflow',
            'account': 'Revenue 4717',
            'customer': milestone['customer'],
            'status': status,
            'payment_terms': 'NET30',
            'contract_type': 'milestone',
            'month': milestone['month'],
            'quarter': f"Q{(milestone['month']-1)//3 + 1}",
            'service_category': 'Strategic Project'
        })
        
        transaction_id += 1
    
    # Sort by date
    revenue_transactions.sort(key=lambda x: x['date'])
    
    # Calculate summary statistics
    total_revenue = sum(t['amount'] for t in revenue_transactions)
    monthly_averages = {}
    quarterly_totals = {}
    
    for month in range(1, 13):
        month_revenue = sum(t['amount'] for t in revenue_transactions if t['month'] == month)
        monthly_averages[f"Month_{month:02d}"] = month_revenue
        
        quarter = f"Q{(month-1)//3 + 1}"
        if quarter not in quarterly_totals:
            quarterly_totals[quarter] = 0
        quarterly_totals[quarter] += month_revenue
    
    # Customer analysis
    customer_totals = {}
    for transaction in revenue_transactions:
        customer = transaction['customer']
        if customer not in customer_totals:
            customer_totals[customer] = 0
        customer_totals[customer] += transaction['amount']
    
    # Sort customers by revenue
    top_customers = sorted(customer_totals.items(), key=lambda x: x[1], reverse=True)
    
    print(f"*** Revenue 4717 Dataset Generated for 2025 ***")
    print(f"Total Transactions: {len(revenue_transactions)}")
    print(f"Total Revenue: ${total_revenue:,.2f}")
    print(f"Average Monthly Revenue: ${total_revenue/12:,.2f}")
    print(f"Date Range: {min(t['date'] for t in revenue_transactions)} to {max(t['date'] for t in revenue_transactions)}")
    print(f"\nQuarterly Breakdown:")
    for quarter, total in quarterly_totals.items():
        print(f"  {quarter}: ${total:,.2f}")
    print(f"\nTop 5 Customers by Revenue:")
    for i, (customer, total) in enumerate(top_customers[:5], 1):
        print(f"  {i}. {customer}: ${total:,.2f}")
    
    # Service category breakdown
    category_totals = {}
    for transaction in revenue_transactions:
        category = transaction['service_category']
        if category not in category_totals:
            category_totals[category] = 0
        category_totals[category] += transaction['amount']
    
    top_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
    print(f"\nTop Service Categories:")
    for i, (category, total) in enumerate(top_categories[:5], 1):
        print(f"  {i}. {category}: ${total:,.2f}")
    
    return revenue_transactions

def update_excel_with_revenue_data():
    """Update the existing Excel file with comprehensive Revenue 4717 data"""
    
    # Generate revenue data
    revenue_data = generate_revenue_4717_dataset()
    
    # Load existing Excel data
    excel_path = os.path.join('static', 'uploads', 'qa_data.xlsx')
    
    try:
        # Read existing sheets
        existing_data = pd.read_excel(excel_path, sheet_name=None)
        
        # Create comprehensive cash flow data combining existing + new revenue
        all_cash_flow_data = []
        
        # Add existing non-4717 cash flow data
        if 'CashFlow' in existing_data:
            existing_cf = existing_data['CashFlow'].to_dict('records')
            for record in existing_cf:
                if record.get('account') != 'Revenue 4717':
                    all_cash_flow_data.append(record)
        
        # Add new Revenue 4717 data
        all_cash_flow_data.extend(revenue_data)
        
        # Sort all data by date
        all_cash_flow_data.sort(key=lambda x: x['date'])
        
        # Create DataFrames
        transactions_df = pd.DataFrame(existing_data.get('Transactions', []).to_dict('records')) if 'Transactions' in existing_data else pd.DataFrame()
        purchase_orders_df = pd.DataFrame(existing_data.get('PurchaseOrders', []).to_dict('records')) if 'PurchaseOrders' in existing_data else pd.DataFrame()
        users_df = pd.DataFrame(existing_data.get('Users', []).to_dict('records')) if 'Users' in existing_data else pd.DataFrame()
        cash_flow_df = pd.DataFrame(all_cash_flow_data)
        
        # Create new Excel file with updated data
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # Write all sheets
            if not transactions_df.empty:
                transactions_df.to_excel(writer, sheet_name='Transactions', index=False)
            if not purchase_orders_df.empty:
                purchase_orders_df.to_excel(writer, sheet_name='PurchaseOrders', index=False)
            if not users_df.empty:
                users_df.to_excel(writer, sheet_name='Users', index=False)
            cash_flow_df.to_excel(writer, sheet_name='CashFlow', index=False)
            
            # Format CashFlow sheet
            cash_flow_sheet = writer.sheets['CashFlow']
            cash_flow_sheet.column_dimensions['A'].width = 10  # ID
            cash_flow_sheet.column_dimensions['B'].width = 12  # Date
            cash_flow_sheet.column_dimensions['C'].width = 50  # Description
            cash_flow_sheet.column_dimensions['D'].width = 15  # Amount
            cash_flow_sheet.column_dimensions['E'].width = 12  # Type
            cash_flow_sheet.column_dimensions['F'].width = 20  # Account
            cash_flow_sheet.column_dimensions['G'].width = 25  # Customer
            cash_flow_sheet.column_dimensions['H'].width = 15  # Status
            cash_flow_sheet.column_dimensions['I'].width = 20  # Payment Terms
            cash_flow_sheet.column_dimensions['J'].width = 15  # Contract Type
            cash_flow_sheet.column_dimensions['K'].width = 10  # Month
            cash_flow_sheet.column_dimensions['L'].width = 10  # Quarter
            cash_flow_sheet.column_dimensions['M'].width = 25  # Service Category
        
        print(f"*** Excel file updated: {excel_path}")
        print(f"*** Total CashFlow records: {len(all_cash_flow_data)}")
        
        # Calculate final totals
        total_inflows = sum(cf['amount'] for cf in all_cash_flow_data if cf['type'] == 'inflow')
        total_outflows = sum(cf['amount'] for cf in all_cash_flow_data if cf['type'] == 'outflow')
        revenue_4717_total = sum(cf['amount'] for cf in all_cash_flow_data if cf.get('account') == 'Revenue 4717')
        
        print(f"*** Final Summary:")
        print(f"   • Total Cash Inflows: ${total_inflows:,.2f}")
        print(f"   • Total Cash Outflows: ${total_outflows:,.2f}")
        print(f"   • Net Cash Flow: ${total_inflows - total_outflows:,.2f}")
        print(f"   • Revenue 4717 Total: ${revenue_4717_total:,.2f}")
        
    except Exception as e:
        print(f"Error updating Excel file: {e}")
        # Create new file if update fails
        cash_flow_df = pd.DataFrame(revenue_data)
        cash_flow_df.to_excel(excel_path, sheet_name='CashFlow', index=False)
        print(f"Created new Excel file with Revenue 4717 data: {excel_path}")

if __name__ == "__main__":
    update_excel_with_revenue_data()