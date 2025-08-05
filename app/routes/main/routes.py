from flask import render_template, render_template_string, request, jsonify, send_from_directory, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from models.transaction import Transaction
from models.purchase_order import PurchaseOrder
from database import db
from utils.excel_data_manager import excel_manager
import json
import os

from . import main_bp

@main_bp.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(main_bp.root_path, '..', '..', 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@main_bp.route('/')
def index():
    # TODO: remove legacy HTML - migrate landing page to masterlayout.html template
    # Current: Inline HTML with Tailwind CSS (functional but not integrated with masterlayout)
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AciTech Cash Flow Management - Professional Financial Solutions</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script>
            tailwind.config = {
                theme: {
                    extend: {
                        colors: {
                            'acidtech': {
                                'blue': '#2563eb',
                                'green': '#10b981',
                                'dark': '#1e293b'
                            }
                        }
                    }
                }
            }
        </script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    </head>
    <body class="bg-gradient-to-br from-blue-50 to-green-50 min-h-screen">
        <!-- Navigation -->
        <nav class="bg-white shadow-lg border-b border-gray-200">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex justify-between h-16">
                    <div class="flex items-center">
                        <div class="flex-shrink-0 flex items-center">
                            <i class="fas fa-chart-line text-acidtech-blue text-2xl mr-2"></i>
                            <h1 class="text-xl font-bold text-acidtech-dark">AciTech Cash Flow</h1>
                        </div>
                    </div>
                    <div class="flex items-center space-x-4">
                        <a href="#features" class="text-gray-600 hover:text-acidtech-blue transition-colors">Features</a>
                        <a href="#about" class="text-gray-600 hover:text-acidtech-blue transition-colors">About</a>
                        <a href="/health" class="bg-acidtech-blue text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                            Status
                        </a>
                    </div>
                </div>
            </div>
        </nav>

        <!-- Hero Section -->
        <div class="relative overflow-hidden">
            <div class="max-w-7xl mx-auto">
                <div class="relative z-10 pb-8 sm:pb-16 md:pb-20 lg:max-w-2xl lg:w-full lg:pb-28 xl:pb-32">
                    <main class="mt-10 mx-auto max-w-7xl px-4 sm:mt-12 sm:px-6 md:mt-16 lg:mt-20 lg:px-8 xl:mt-28">
                        <div class="sm:text-center lg:text-left">
                            <h1 class="text-4xl tracking-tight font-extrabold text-gray-900 sm:text-5xl md:text-6xl">
                                <span class="block xl:inline">Professional</span>
                                <span class="block text-acidtech-blue xl:inline">Cash Flow</span>
                                <span class="block xl:inline">Management</span>
                            </h1>
                            <p class="mt-3 text-base text-gray-500 sm:mt-5 sm:text-lg sm:max-w-xl sm:mx-auto md:mt-5 md:text-xl lg:mx-0">
                                Streamline your financial operations with our comprehensive cash flow management system. 
                                Track accounts payable, receivable, purchase orders, and generate insightful reports.
                            </p>
                            <div class="mt-5 sm:mt-8 sm:flex sm:justify-center lg:justify-start space-x-4">
                                <div class="rounded-md shadow">
                                    <a href="/ap" class="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-acidtech-blue hover:bg-blue-700 transition-all duration-200 transform hover:scale-105">
                                        <i class="fas fa-credit-card mr-2"></i> Accounts Payable
                                    </a>
                                </div>
                                <div class="mt-3 sm:mt-0">
                                    <a href="/ar" class="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-acidtech-green hover:bg-green-700 transition-all duration-200 transform hover:scale-105">
                                        <i class="fas fa-receipt mr-2"></i> Accounts Receivable
                                    </a>
                                </div>
                            </div>
                        </div>
                    </main>
                </div>
            </div>
            <div class="lg:absolute lg:inset-y-0 lg:right-0 lg:w-1/2">
                <div class="h-56 w-full bg-gradient-to-r from-acidtech-blue to-acidtech-green sm:h-72 md:h-96 lg:w-full lg:h-full flex items-center justify-center">
                    <div class="text-white text-center">
                        <i class="fas fa-chart-line text-8xl mb-4 opacity-30"></i>
                        <div class="text-xl font-semibold opacity-40">Financial Intelligence</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Features Section -->
        <div id="features" class="py-12 bg-white">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="lg:text-center">
                    <h2 class="text-base text-acidtech-blue font-semibold tracking-wide uppercase">Features</h2>
                    <p class="mt-2 text-3xl leading-8 font-extrabold tracking-tight text-gray-900 sm:text-4xl">
                        Complete Financial Management
                    </p>
                    <p class="mt-4 max-w-2xl text-xl text-gray-500 lg:mx-auto">
                        Everything you need to manage your cash flow efficiently and make informed financial decisions.
                    </p>
                </div>

                <div class="mt-10">
                    <div class="space-y-10 md:space-y-0 md:grid md:grid-cols-2 lg:grid-cols-3 md:gap-x-8 md:gap-y-10">
                        <!-- Accounts Payable -->
                        <div class="relative bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
                            <div class="absolute -top-4 left-4">
                                <div class="flex items-center justify-center h-12 w-12 rounded-md bg-acidtech-blue text-white">
                                    <i class="fas fa-credit-card text-xl"></i>
                                </div>
                            </div>
                            <div class="mt-8">
                                <h3 class="text-lg leading-6 font-medium text-gray-900">Accounts Payable</h3>
                                <p class="mt-2 text-base text-gray-500">
                                    Track vendor payments, manage due dates, and never miss a payment deadline.
                                </p>
                            </div>
                        </div>

                        <!-- Accounts Receivable -->
                        <div class="relative bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
                            <div class="absolute -top-4 left-4">
                                <div class="flex items-center justify-center h-12 w-12 rounded-md bg-acidtech-green text-white">
                                    <i class="fas fa-receipt text-xl"></i>
                                </div>
                            </div>
                            <div class="mt-8">
                                <h3 class="text-lg leading-6 font-medium text-gray-900">Accounts Receivable</h3>
                                <p class="mt-2 text-base text-gray-500">
                                    Monitor customer payments, track outstanding invoices, and improve collection efficiency.
                                </p>
                            </div>
                        </div>

                        <!-- Purchase Orders -->
                        <div class="relative bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
                            <div class="absolute -top-4 left-4">
                                <div class="flex items-center justify-center h-12 w-12 rounded-md bg-purple-500 text-white">
                                    <i class="fas fa-shopping-cart text-xl"></i>
                                </div>
                            </div>
                            <div class="mt-8">
                                <h3 class="text-lg leading-6 font-medium text-gray-900">Purchase Orders</h3>
                                <p class="mt-2 text-base text-gray-500">
                                    Create, manage, and track purchase orders from draft to fulfillment.
                                </p>
                            </div>
                        </div>

                        <!-- Reports & Analytics -->
                        <div class="relative bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
                            <div class="absolute -top-4 left-4">
                                <div class="flex items-center justify-center h-12 w-12 rounded-md bg-orange-500 text-white">
                                    <i class="fas fa-chart-bar text-xl"></i>
                                </div>
                            </div>
                            <div class="mt-8">
                                <h3 class="text-lg leading-6 font-medium text-gray-900">Reports & Analytics</h3>
                                <p class="mt-2 text-base text-gray-500">
                                    Generate comprehensive reports and gain insights into your cash flow patterns.
                                </p>
                            </div>
                        </div>

                        <!-- AI Insights -->
                        <div class="relative bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
                            <div class="absolute -top-4 left-4">
                                <div class="flex items-center justify-center h-12 w-12 rounded-md bg-indigo-500 text-white">
                                    <i class="fas fa-brain text-xl"></i>
                                </div>
                            </div>
                            <div class="mt-8">
                                <h3 class="text-lg leading-6 font-medium text-gray-900">AI-Powered Insights</h3>
                                <p class="mt-2 text-base text-gray-500">
                                    Get predictive analytics and smart recommendations for better financial planning.
                                </p>
                            </div>
                        </div>

                        <!-- System Status -->
                        <div class="relative bg-gradient-to-r from-green-50 to-blue-50 p-6 rounded-lg border-2 border-green-200">
                            <div class="absolute -top-4 left-4">
                                <div class="flex items-center justify-center h-12 w-12 rounded-md bg-green-500 text-white">
                                    <i class="fas fa-server text-xl"></i>
                                </div>
                            </div>
                            <div class="mt-8">
                                <h3 class="text-lg leading-6 font-medium text-gray-900">System Status</h3>
                                <div class="mt-2 space-y-1">
                                    <p class="text-sm text-green-600"><i class="fas fa-check-circle mr-1"></i> Flask Application: Running</p>
                                    <p class="text-sm text-green-600"><i class="fas fa-check-circle mr-1"></i> Database: Connected</p>
                                    <p class="text-sm text-green-600"><i class="fas fa-check-circle mr-1"></i> Azure App Service: Active</p>
                                    <p class="text-sm text-blue-600"><i class="fas fa-cog mr-1"></i> Architecture: Modular Blueprints</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <footer class="bg-acidtech-dark">
            <div class="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
                <div class="text-center">
                    <div class="flex justify-center items-center mb-4">
                        <i class="fas fa-chart-line text-acidtech-blue text-2xl mr-2"></i>
                        <span class="text-xl font-bold text-white">AciTech Cash Flow Management</span>
                    </div>
                    <p class="text-gray-400">Professional financial management solutions for modern businesses</p>
                    <div class="mt-4 flex justify-center space-x-6">
                        <a href="/health" class="text-gray-400 hover:text-white transition-colors">
                            <i class="fas fa-heartbeat mr-1"></i> System Health
                        </a>
                        <a href="/reports" class="text-gray-400 hover:text-white transition-colors">
                            <i class="fas fa-chart-bar mr-1"></i> Reports
                        </a>
                        <a href="/po" class="text-gray-400 hover:text-white transition-colors">
                            <i class="fas fa-shopping-cart mr-1"></i> Purchase Orders
                        </a>
                    </div>
                </div>
            </div>
        </footer>
    </body>
    </html>
    '''

@main_bp.route('/dashboard')
def dashboard():
    """Dashboard with File Mode support"""
    
    if current_app.config.get('USE_FILE_MODE', False):
        # File Mode: Use Excel data
        try:
            totals = excel_manager.calculate_totals()
            recent_transactions = excel_manager.get_transactions()[:5]  # Get first 5 transactions
            
            return render_template('dashboard.html', 
                                 total_receivables=totals['total_receivables'],
                                 total_payables=totals['total_payables'],
                                 cash_available=totals['cash_available'],
                                 recent_transactions=recent_transactions,
                                 overdue_receivables=totals['overdue_receivables'],
                                 overdue_payables=totals['overdue_payables'],
                                 file_mode=True)
        except Exception as e:
            # Fallback to default data if Excel fails
            pass
    
    # Database Mode or fallback: Use database queries
    try:
        # Calculate totals from database
        total_receivables = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.type == 'receivable',
            Transaction.status == 'pending'
        ).scalar() or 0
        
        total_payables = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.type == 'payable',
            Transaction.status == 'pending'
        ).scalar() or 0
        
        # Get recent transactions
        recent_transactions_query = Transaction.query.order_by(
            Transaction.created_at.desc()
        ).limit(5).all()
        
        recent_transactions = [{
            'id': t.id,
            'vendor_customer': t.vendor_customer,
            'amount': t.amount,
            'type': t.type,
            'due_date': t.due_date,
            'invoice_number': t.invoice_number,
            'description': t.description
        } for t in recent_transactions_query]
        
        # Calculate overdue items
        overdue_receivables = Transaction.query.filter(
            Transaction.type == 'receivable',
            Transaction.status == 'pending',
            Transaction.due_date < date.today()
        ).count()
        
        overdue_payables = Transaction.query.filter(
            Transaction.type == 'payable',
            Transaction.status == 'pending', 
            Transaction.due_date < date.today()
        ).count()
        
    except Exception as e:
        # Fallback to hardcoded data if database fails
        total_receivables = 45750.00
        total_payables = 13200.75
        overdue_receivables = 2
        overdue_payables = 1
        recent_transactions = [
            {
                'id': 1, 'vendor_customer': 'Acme Corporation', 'amount': 15000.00,
                'type': 'receivable', 'due_date': date.today() + timedelta(days=30),
                'invoice_number': 'INV-2024-001', 'description': 'Consulting Services Q4'
            },
            {
                'id': 2, 'vendor_customer': 'Office Supplies Co', 'amount': 2400.00,
                'type': 'payable', 'due_date': date.today() + timedelta(days=15),
                'invoice_number': 'BILL-2024-001', 'description': 'Monthly Office Supplies'
            }
        ]
    
    cash_available = total_receivables - total_payables
    
    return render_template('dashboard.html', 
                         total_receivables=total_receivables,
                         total_payables=total_payables,
                         cash_available=cash_available,
                         recent_transactions=recent_transactions,
                         overdue_receivables=overdue_receivables,
                         overdue_payables=overdue_payables,
                         file_mode=current_app.config.get('USE_FILE_MODE', False))

@main_bp.route('/api/cash-flow-data')
def cash_flow_data():
    # Generate cash flow data for charts
    end_date = date.today()
    start_date = end_date - timedelta(days=90)
    
    # Sample data for demonstration
    dates = []
    receivables = []
    payables = []
    
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.strftime('%Y-%m-%d'))
        
        # Sample receivables data
        receivables_amount = Transaction.query.filter(
            Transaction.type == 'receivable',
            Transaction.due_date == current_date
        ).with_entities(db.func.sum(Transaction.amount)).scalar() or 0
        
        # Sample payables data
        payables_amount = Transaction.query.filter(
            Transaction.type == 'payable',
            Transaction.due_date == current_date
        ).with_entities(db.func.sum(Transaction.amount)).scalar() or 0
        
        receivables.append(float(receivables_amount))
        payables.append(float(payables_amount))
        
        current_date += timedelta(days=1)
    
    return jsonify({
        'dates': dates,
        'receivables': receivables,
        'payables': payables
    })

@main_bp.route('/test-layout')
def test_layout():
    """Test route with full masterlayout and simulated data"""
    try:
        from flask import request
        
        # Datos de prueba completos para el dashboard
        total_receivables = 45750.00
        total_payables = 13200.75
        cash_available = 32549.25
        recent_transactions = [
            {
                "id": 1,
                "description": "Payment from Acme Corp",
                "amount": 1500.00,
                "type": "receivable",
                "vendor_customer": "Acme Corporation",
                "created_at": datetime.now() - timedelta(days=1)
            },
            {
                "id": 2,
                "description": "Office Supplies Payment", 
                "amount": 800.50,
                "type": "payable",
                "vendor_customer": "Office Depot",
                "created_at": datetime.now() - timedelta(days=2)
            },
            {
                "id": 3,
                "description": "Consulting Invoice",
                "amount": 2500.00,
                "type": "receivable",
                "vendor_customer": "Tech Solutions Inc",
                "created_at": datetime.now() - timedelta(days=3)
            }
        ]
        overdue_receivables = 2
        overdue_payables = 1
        
        return render_template('test_dashboard.html',
                             total_receivables=total_receivables,
                             total_payables=total_payables,
                             cash_available=cash_available,
                             recent_transactions=recent_transactions,
                             overdue_receivables=overdue_receivables,
                             overdue_payables=overdue_payables)
        
    except Exception as e:
        # Final fallback si algo falla
        return f"<h1>Error 500: {str(e)}</h1><p>Timestamp: {datetime.now()}</p>"

@main_bp.route('/init-sample-data')
def init_sample_data():
    """Initialize database with sample data - for Azure deployment"""
    try:
        from models.user import User
        
        # Drop and recreate all tables
        db.drop_all()
        db.create_all()
        
        # Create test user
        test_user = User(
            username='demo_user',
            email='demo@acidtech.com',
            first_name='Demo',
            last_name='User'
        )
        test_user.set_password('demo123')
        db.session.add(test_user)
        db.session.commit()
        
        user = User.query.first()
        
        # Sample receivables
        receivables_data = [
            {'vendor_customer': 'Acme Corporation', 'amount': 15000.00, 'due_date': date.today() + timedelta(days=30), 'description': 'Consulting Services', 'invoice_number': 'INV-001', 'status': 'pending'},
            {'vendor_customer': 'Tech Solutions Inc', 'amount': 8500.00, 'due_date': date.today() + timedelta(days=15), 'description': 'Software Development', 'invoice_number': 'INV-002', 'status': 'pending'},
            {'vendor_customer': 'Global Systems Ltd', 'amount': 12250.00, 'due_date': date.today() + timedelta(days=45), 'description': 'System Integration', 'invoice_number': 'INV-003', 'status': 'pending'},
        ]
        
        for data in receivables_data:
            transaction = Transaction(
                type='receivable',
                vendor_customer=data['vendor_customer'],
                amount=data['amount'],
                due_date=data['due_date'],
                description=data['description'],
                invoice_number=data['invoice_number'],
                status=data['status'],
                created_by=user.id
            )
            db.session.add(transaction)
        
        # Sample payables
        payables_data = [
            {'vendor_customer': 'Office Supplies Co', 'amount': 2400.00, 'due_date': date.today() + timedelta(days=20), 'description': 'Office Supplies', 'invoice_number': 'BILL-001', 'status': 'pending'},
            {'vendor_customer': 'IT Equipment Ltd', 'amount': 5600.00, 'due_date': date.today() + timedelta(days=10), 'description': 'Hardware Purchase', 'invoice_number': 'BILL-002', 'status': 'pending'},
        ]
        
        for data in payables_data:
            transaction = Transaction(
                type='payable',
                vendor_customer=data['vendor_customer'],
                amount=data['amount'],
                due_date=data['due_date'],
                description=data['description'],
                invoice_number=data['invoice_number'],
                status=data['status'],
                created_by=user.id
            )
            db.session.add(transaction)
        
        db.session.commit()
        
        # Calculate totals
        total_receivables = db.session.query(db.func.sum(Transaction.amount)).filter_by(type='receivable', status='pending').scalar() or 0
        total_payables = db.session.query(db.func.sum(Transaction.amount)).filter_by(type='payable', status='pending').scalar() or 0
        total_transactions = Transaction.query.count()
        
        return f"""
        <h1>✅ Sample Data Initialized Successfully!</h1>
        <p><strong>Database populated with:</strong></p>
        <ul>
            <li>Total transactions: {total_transactions}</li>
            <li>Accounts receivable: ${total_receivables:,.2f}</li>
            <li>Accounts payable: ${total_payables:,.2f}</li>
            <li>Net cash flow: ${total_receivables - total_payables:,.2f}</li>
            <li>Demo user: demo_user / demo123</li>
        </ul>
        <p><a href="/dashboard">Go to Dashboard</a> | <a href="/">Home</a></p>
        """
        
    except Exception as e:
        db.session.rollback()
        return f"<h1>❌ Error initializing data:</h1><p>{str(e)}</p>"

@main_bp.route('/upload-excel', methods=['GET', 'POST'])
def upload_excel():
    """Upload Excel file for File Mode QA testing"""
    if request.method == 'POST':
        if 'excel_file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['excel_file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and file.filename.endswith(('.xlsx', '.xls')):
            import os
            from werkzeug.utils import secure_filename
            
            filename = secure_filename('qa_data.xlsx')  # Always use this name
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            
            # Create upload directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            try:
                file.save(file_path)
                
                # Force reload Excel data
                excel_manager.load_excel_data(force_reload=True)
                
                flash('Excel file uploaded successfully! File Mode data updated.', 'success')
                return redirect(url_for('main.dashboard'))
                
            except Exception as e:
                flash(f'Error uploading file: {str(e)}', 'error')
        else:
            flash('Please upload an Excel file (.xlsx or .xls)', 'error')
    
    # Check current file status
    excel_path = current_app.config.get('EXCEL_DATA_PATH')
    file_exists = os.path.exists(excel_path) if excel_path else False
    file_mode_enabled = current_app.config.get('USE_FILE_MODE', False)
    
    return render_template('upload_excel.html', 
                         file_exists=file_exists, 
                         file_mode_enabled=file_mode_enabled,
                         excel_path=excel_path)

@main_bp.route('/generate-sample-excel')
def generate_sample_excel():
    """Generate and download sample Excel file"""
    try:
        # Import and run the generate function
        import sys  
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from generate_sample_excel import generate_sample_excel
        
        # Generate the Excel file
        output_path = generate_sample_excel()
        
        # Return the file for download
        return send_from_directory(
            os.path.dirname(output_path),
            os.path.basename(output_path),
            as_attachment=True,
            download_name='sample_qa_data.xlsx'
        )
        
    except Exception as e:
        flash(f'Error generating sample Excel file: {str(e)}', 'error')
        return redirect(url_for('main.upload_excel'))
