# AciTech Cash Flow Management System

A comprehensive, professional Flask web application for managing cash flow, accounts payable, accounts receivable, and purchase orders. Built with modern web technologies and featuring AI-powered analytics.

## 🚀 Features

### Core Functionality
- **Accounts Payable Management**: Track and manage vendor payments and bills
- **Accounts Receivable Management**: Monitor customer payments and invoices
- **Purchase Order System**: Create, manage, and track purchase orders from draft to fulfillment
- **Cash Flow Reporting**: Generate comprehensive reports and visualizations
- **Document Management**: Upload and manage receipts and invoices

### Advanced Features
- **AI-Powered Predictions**: Machine learning-based cash flow forecasting
- **Risk Analysis**: Automated risk assessment and recommendations
- **Responsive Design**: Mobile-friendly interface using Tailwind CSS
- **Azure Integration**: Cloud storage and key vault integration
- **OCR Processing**: Extract data from uploaded documents
- **Interactive Charts**: Real-time data visualization with Plotly

## 🛠 Technology Stack

- **Backend**: Flask 3.0, SQLAlchemy, Flask-Login
- **Frontend**: HTML5, Tailwind CSS, JavaScript
- **Database**: SQLite (development) / Azure SQL (production)
- **Cloud**: Microsoft Azure integration
- **Charts**: Plotly.js for interactive visualizations
- **Icons**: Font Awesome

## 📦 Installation

### Prerequisites
- Python 3.11+
- Node.js (for Tailwind CSS)
- Git

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Jaimikoko/acidtech-cashflow-app.git
   cd acidtech-cashflow-app
   ```

2. **Set up Python virtual environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\\Scripts\\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Node.js dependencies (for Tailwind CSS)**
   ```bash
   npm install
   ```

5. **Initialize the database**
   ```bash
   python init_db.py
   ```

6. **Run the application**
   ```bash
   python run.py
   ```

7. **Access the application**
   - Open your browser and navigate to `http://localhost:5000`

## 👥 Default Users

The system comes with pre-configured demo users:

- **Admin User**
  - Username: `admin`
  - Password: `admin123`

- **Demo User**
  - Username: `demo`  
  - Password: `demo123`

## 🌐 Deployment

### Azure App Service Deployment

The application is configured for deployment to Azure App Service with GitHub Actions.

1. **Configure Azure services** (names can be customized):
   - App Service: `acidtech-prod-app`
   - Storage Account: `acidtechprod45584`
   - Key Vault: `acidtech-prod-kv`
   - Application Insights: `acidtech-prod-insights`

2. **Set up GitHub Secrets**:
   - `AZURE_WEBAPP_PUBLISH_PROFILE`: Download from Azure App Service

3. **Deploy**: Push to the `main` branch to trigger automatic deployment

### Environment Variables

Configure these environment variables for production:

```env
SECRET_KEY=your-production-secret-key
AZURE_STORAGE_CONNECTION_STRING=your-azure-storage-connection
AZURE_KEY_VAULT_URL=https://your-keyvault.vault.azure.net/
APPINSIGHTS_CONNECTION_STRING=your-app-insights-connection-string
```

## 📊 Sample Data

The application includes comprehensive sample data:
- 5 Accounts Payable transactions
- 5 Accounts Receivable transactions  
- 3 Purchase Orders with line items
- Demo users with different roles

## 🔧 Configuration

### Database Configuration
- **Development**: SQLite database (`app.db`)
- **Production**: Configure `DATABASE_URL` for your production database

### File Uploads
- **Local**: Files stored in `app/static/uploads/`
- **Production**: Files stored in Azure Blob Storage

### AI Features
The AI predictor analyzes:
- Historical payment patterns
- Cash flow trends
- Risk assessment
- Vendor/customer insights

## 📱 User Interface

### Design Features
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Color Scheme**: Green, blue, and white theme
- **Modern UI**: Clean, professional interface
- **Interactive Elements**: Hover effects, smooth transitions
- **Accessibility**: WCAG 2.1 compliant

### Key Pages
- **Dashboard**: Overview with KPIs and charts
- **Accounts Payable**: Vendor payment management
- **Accounts Receivable**: Customer payment tracking
- **Purchase Orders**: Order management system
- **Reports**: Analytics and insights
- **AI Insights**: Predictive analytics dashboard

## 🔒 Security Features

- User authentication and session management
- Role-based access control
- Secure file upload handling
- CSRF protection
- SQL injection prevention
- XSS protection

## 🧪 Testing

Run the application locally and test the following workflows:

1. **User Registration/Login**
2. **Add Payable Transaction** with file upload
3. **Add Receivable Transaction** 
4. **Create Purchase Order** with multiple line items
5. **View Reports** and cash flow charts
6. **AI Insights** page for predictions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an [Issue](https://github.com/Jaimikoko/acidtech-cashflow-app/issues)
- Email: admin@acidtech.com

## 🔄 Version History

- **v1.0.2** - Modular Architecture and Flask-Login ✅
  - Implemented modular Flask architecture with organized blueprints
  - Configured Flask-Login properly to eliminate warnings
  - Added factory pattern for better app organization
  - User authentication system ready with test accounts

- **v1.0.1** - Templates fix and Python 3.11 compatibility ✅
  - Fixed missing templates causing Error 500
  - Python 3.11 container rebuild resolved
  - All 20 templates deployed successfully
  - Application fully functional on Azure

- **v1.0.0** - Initial release with complete cash flow management system
  - Full CRUD operations for AP/AR/PO
  - AI-powered analytics
  - Azure cloud integration
  - Responsive web design

---

**Built with ❤️ by AciTech**

🤖 *Generated with [Claude Code](https://claude.ai/code)*