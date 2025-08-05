from flask import render_template, request, flash, redirect, url_for, jsonify
from datetime import datetime, date
import csv
import io
import uuid
from database import db
from models.bank_transaction import BankTransaction

from . import data_import_bp

@data_import_bp.route('/')
def index():
    """Data Import main page - Admin only"""
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Data Import - AciTech Cash Flow Management</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script>
            tailwind.config = {{
                theme: {{
                    extend: {{
                        colors: {{
                            'acidtech': {{
                                'blue': '#2563eb',
                                'green': '#10b981',
                                'dark': '#1e293b'
                            }}
                        }}
                    }}
                }}
            }}
        </script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    </head>
    <body class="bg-gray-50 min-h-screen">
        <div class="min-h-screen bg-gray-50 py-8">
            <!-- Header -->
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="bg-white shadow rounded-lg mb-6">
                    <div class="px-6 py-4 border-b border-gray-200">
                        <div class="flex items-center justify-between">
                            <div>
                                <h1 class="text-2xl font-bold text-gray-900">Data Import Center</h1>
                                <p class="text-gray-600">Import bank statements and financial data</p>
                            </div>
                            <div class="flex items-center space-x-4">
                                <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                                    <i class="fas fa-shield-alt mr-1"></i>Admin Only
                                </span>
                                <a href="/dashboard" class="text-gray-600 hover:text-gray-800">
                                    <i class="fas fa-arrow-left mr-2"></i>Back to Dashboard
                                </a>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Bank Accounts Grid -->
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    <!-- Income 4717 -->
                    <div class="bg-white rounded-xl shadow-lg p-6 border-t-4 border-green-500">
                        <div class="flex items-center justify-between mb-4">
                            <div>
                                <h3 class="text-lg font-semibold text-gray-900">Income 4717</h3>
                                <p class="text-sm text-gray-500">Revenue & Receipts</p>
                            </div>
                            <div class="bg-green-100 rounded-full p-3">
                                <i class="fas fa-arrow-down text-green-600 text-xl"></i>
                            </div>
                        </div>
                        <div class="space-y-2 text-sm text-gray-600">
                            <p><i class="fas fa-check text-green-500 mr-2"></i>Client payments</p>
                            <p><i class="fas fa-check text-green-500 mr-2"></i>Service income</p>
                            <p><i class="fas fa-check text-green-500 mr-2"></i>Interest income</p>
                        </div>
                        <button onclick="openImportModal('Income 4717', 'INCOME')" 
                                class="mt-4 w-full bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 transition-colors">
                            <i class="fas fa-upload mr-2"></i>Import Data
                        </button>
                    </div>

                    <!-- Bill Pay 4091 -->
                    <div class="bg-white rounded-xl shadow-lg p-6 border-t-4 border-red-500">
                        <div class="flex items-center justify-between mb-4">
                            <div>
                                <h3 class="text-lg font-semibold text-gray-900">Bill Pay 4091</h3>
                                <p class="text-sm text-gray-500">Bills & Expenses</p>
                            </div>
                            <div class="bg-red-100 rounded-full p-3">
                                <i class="fas fa-arrow-up text-red-600 text-xl"></i>
                            </div>
                        </div>
                        <div class="space-y-2 text-sm text-gray-600">
                            <p><i class="fas fa-check text-red-500 mr-2"></i>Utilities</p>
                            <p><i class="fas fa-check text-red-500 mr-2"></i>Rent payments</p>
                            <p><i class="fas fa-check text-red-500 mr-2"></i>Professional services</p>
                        </div>
                        <button onclick="openImportModal('Bill Pay 4091', 'EXPENSE')" 
                                class="mt-4 w-full bg-red-600 text-white py-2 px-4 rounded-lg hover:bg-red-700 transition-colors">
                            <i class="fas fa-upload mr-2"></i>Import Data
                        </button>
                    </div>

                    <!-- Payroll 4709 -->
                    <div class="bg-white rounded-xl shadow-lg p-6 border-t-4 border-blue-500">
                        <div class="flex items-center justify-between mb-4">
                            <div>
                                <h3 class="text-lg font-semibold text-gray-900">Payroll 4709</h3>
                                <p class="text-sm text-gray-500">Payroll & Benefits</p>
                            </div>
                            <div class="bg-blue-100 rounded-full p-3">
                                <i class="fas fa-users text-blue-600 text-xl"></i>
                            </div>
                        </div>
                        <div class="space-y-2 text-sm text-gray-600">
                            <p><i class="fas fa-check text-blue-500 mr-2"></i>Employee salaries</p>
                            <p><i class="fas fa-check text-blue-500 mr-2"></i>Benefits</p>
                            <p><i class="fas fa-check text-blue-500 mr-2"></i>Payroll taxes</p>
                        </div>
                        <button onclick="openImportModal('Payroll 4709', 'PAYROLL')" 
                                class="mt-4 w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors">
                            <i class="fas fa-upload mr-2"></i>Import Data
                        </button>
                    </div>

                    <!-- CC-Capital One -->
                    <div class="bg-white rounded-xl shadow-lg p-6 border-t-4 border-purple-500">
                        <div class="flex items-center justify-between mb-4">
                            <div>
                                <h3 class="text-lg font-semibold text-gray-900">CC-Capital One</h3>
                                <p class="text-sm text-gray-500">Credit Card</p>
                            </div>
                            <div class="bg-purple-100 rounded-full p-3">
                                <i class="fas fa-credit-card text-purple-600 text-xl"></i>
                            </div>
                        </div>
                        <div class="space-y-2 text-sm text-gray-600">
                            <p><i class="fas fa-check text-purple-500 mr-2"></i>Purchases</p>
                            <p><i class="fas fa-check text-purple-500 mr-2"></i>Payments</p>
                            <p><i class="fas fa-check text-purple-500 mr-2"></i>Gas & fuel</p>
                        </div>
                        <button onclick="openImportModal('CC-Capital One', 'CREDIT_CARD')" 
                                class="mt-4 w-full bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 transition-colors">
                            <i class="fas fa-upload mr-2"></i>Import Data
                        </button>
                    </div>
                </div>

                <!-- CSV Format Guide -->
                <div class="bg-white rounded-xl shadow-lg p-6 mb-8">
                    <h3 class="text-lg font-semibold text-gray-900 mb-4">
                        <i class="fas fa-file-csv text-green-600 mr-2"></i>CSV Format Requirements
                    </h3>
                    
                    <div class="bg-gray-50 rounded-lg p-4 mb-4">
                        <h4 class="font-medium text-gray-900 mb-2">Required Columns:</h4>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                            <div>
                                <code class="bg-white px-2 py-1 rounded text-acidtech-blue">Date</code> - Transaction date (YYYY-MM-DD)
                            </div>
                            <div>
                                <code class="bg-white px-2 py-1 rounded text-acidtech-blue">Description</code> - Transaction description
                            </div>
                            <div>
                                <code class="bg-white px-2 py-1 rounded text-acidtech-blue">Amount</code> - Amount (+ for income, - for expenses)
                            </div>
                            <div>
                                <code class="bg-white px-2 py-1 rounded text-acidtech-blue">Type</code> - CREDIT or DEBIT
                            </div>
                            <div>
                                <code class="bg-white px-2 py-1 rounded text-acidtech-blue">Category</code> - Transaction category
                            </div>
                            <div>
                                <code class="bg-white px-2 py-1 rounded text-acidtech-blue">Accounting_Class</code> - Accounting classification
                            </div>
                            <div>
                                <code class="bg-white px-2 py-1 rounded text-acidtech-blue">Reference</code> - Invoice/Check number (optional)
                            </div>
                        </div>
                    </div>

                    <div class="bg-blue-50 rounded-lg p-4">
                        <h4 class="font-medium text-blue-900 mb-2">Sample CSV:</h4>
                        <pre class="text-xs text-blue-800 whitespace-pre-wrap">Date,Description,Amount,Type,Category,Accounting_Class,Reference
2024-01-15,"CLIENT PAYMENT - ACME CORP",8500.00,CREDIT,INCOME,Revenue,INV-001
2024-01-16,"OFFICE RENT PAYMENT",-2800.00,DEBIT,RENT,Facilities,RENT-JAN24
2024-01-17,"GAS STATION FUEL",-85.50,DEBIT,FUEL,Gas & Fuel,CC-001</pre>
                    </div>
                </div>

                <!-- Recent Imports -->
                <div class="bg-white rounded-xl shadow-lg p-6">
                    <h3 class="text-lg font-semibold text-gray-900 mb-4">
                        <i class="fas fa-history text-gray-600 mr-2"></i>Recent Imports
                    </h3>
                    <div class="text-center py-8 text-gray-500">
                        <i class="fas fa-inbox text-4xl mb-4"></i>
                        <p>No imports yet. Upload your first bank statement above.</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Import Modal -->
        <div id="importModal" class="hidden fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div class="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
                <div class="mt-3">
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="text-lg font-semibold text-gray-900" id="modalTitle">Import Bank Statement</h3>
                        <button onclick="closeImportModal()" class="text-gray-400 hover:text-gray-600">
                            <i class="fas fa-times text-xl"></i>
                        </button>
                    </div>
                    
                    <form id="importForm" enctype="multipart/form-data">
                        <input type="hidden" id="accountName" name="account_name">
                        <input type="hidden" id="accountType" name="account_type">
                        
                        <div class="mb-4">
                            <label class="block text-sm font-medium text-gray-700 mb-2">
                                Select CSV File
                            </label>
                            <div class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-acidtech-blue transition-colors">
                                <input type="file" id="csvFile" name="csv_file" accept=".csv" class="hidden" onchange="handleFileSelect(event)">
                                <div id="dropZone" onclick="document.getElementById('csvFile').click()">
                                    <i class="fas fa-cloud-upload-alt text-4xl text-gray-400 mb-4"></i>
                                    <p class="text-sm text-gray-600">Click to select CSV file or drag & drop</p>
                                    <p class="text-xs text-gray-500 mt-2">Maximum file size: 10MB</p>
                                </div>
                                <div id="fileInfo" class="hidden">
                                    <i class="fas fa-file-csv text-green-600 text-2xl mb-2"></i>
                                    <p id="fileName" class="text-sm font-medium text-gray-900"></p>
                                    <p id="fileSize" class="text-xs text-gray-500"></p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="flex justify-end space-x-3">
                            <button type="button" onclick="closeImportModal()" 
                                    class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50">
                                Cancel
                            </button>
                            <button type="submit" id="importBtn" disabled
                                    class="px-4 py-2 bg-acidtech-blue text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed">
                                <i class="fas fa-upload mr-2"></i>Import Data
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <script>
            function openImportModal(accountName, accountType) {{
                document.getElementById('modalTitle').textContent = `Import ${accountName} Statement`;
                document.getElementById('accountName').value = accountName;
                document.getElementById('accountType').value = accountType;
                document.getElementById('importModal').classList.remove('hidden');
            }}

            function closeImportModal() {{
                document.getElementById('importModal').classList.add('hidden');
                document.getElementById('importForm').reset();
                document.getElementById('fileInfo').classList.add('hidden');
                document.getElementById('dropZone').classList.remove('hidden');
                document.getElementById('importBtn').disabled = true;
            }}

            function handleFileSelect(event) {{
                const file = event.target.files[0];
                if (file) {{
                    document.getElementById('fileName').textContent = file.name;
                    document.getElementById('fileSize').textContent = `${(file.size / 1024 / 1024).toFixed(2)} MB`;
                    document.getElementById('fileInfo').classList.remove('hidden');
                    document.getElementById('dropZone').classList.add('hidden');
                    document.getElementById('importBtn').disabled = false;
                }}
            }}

            // Form submission
            document.getElementById('importForm').addEventListener('submit', async function(e) {{
                e.preventDefault();
                
                const formData = new FormData(this);
                const importBtn = document.getElementById('importBtn');
                
                // Show loading state
                importBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Processing...';
                importBtn.disabled = true;
                
                try {{
                    const response = await fetch('/data-import/upload', {{
                        method: 'POST',
                        body: formData
                    }});
                    
                    const result = await response.json();
                    
                    if (result.success) {{
                        alert(`Success! Imported ${result.records_imported} records.`);
                        closeImportModal();
                        location.reload(); // Refresh to show new data
                    }} else {{
                        alert(`Error: ${result.error}`);
                    }}
                }} catch (error) {{
                    alert(`Error: ${error.message}`);
                }} finally {{
                    importBtn.innerHTML = '<i class="fas fa-upload mr-2"></i>Import Data';
                    importBtn.disabled = false;
                }}
            }});
        </script>
    </body>
    </html>
    '''

@data_import_bp.route('/upload', methods=['POST'])
def upload_csv():
    """Process CSV upload and import bank transactions"""
    try:
        # Get form data
        account_name = request.form.get('account_name')
        account_type = request.form.get('account_type')
        csv_file = request.files.get('csv_file')
        
        if not csv_file or not account_name:
            return jsonify({'success': False, 'error': 'Missing required data'})
        
        # Generate batch ID for tracking
        batch_id = str(uuid.uuid4())[:8]
        
        # Read and process CSV
        csv_content = csv_file.read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        
        records_imported = 0
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 because row 1 is header
            try:
                # Parse date
                transaction_date = datetime.strptime(row['Date'], '%Y-%m-%d').date()
                
                # Parse amount
                amount = float(row['Amount'])
                
                # Create bank transaction
                bank_transaction = BankTransaction(
                    account_name=account_name,
                    account_type=account_type,
                    transaction_date=transaction_date,
                    description=row['Description'],
                    amount=amount,
                    transaction_type=row['Type'],
                    category=row.get('Category', ''),
                    accounting_class=row.get('Accounting_Class', ''),
                    reference=row.get('Reference', ''),
                    import_batch_id=batch_id,
                    created_by=1  # TODO: Get from current user when auth is implemented
                )
                
                db.session.add(bank_transaction)
                records_imported += 1
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        # Commit all records
        db.session.commit()
        
        return jsonify({
            'success': True,
            'records_imported': records_imported,
            'batch_id': batch_id,
            'errors': errors
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})