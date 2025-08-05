# QA Testing Guide - AciTech Cash Flow Management

## 🎯 Overview

This guide provides step-by-step instructions for executing Quality Assurance testing on the AciTech Cash Flow Management application, specifically validating the Master Layout System migration from Tailwind CSS to Bootstrap 5.

## 📋 Pre-Testing Setup

### Prerequisites

1. **Python Environment**
   ```bash
   python --version  # Should be 3.11+
   pip install -r tests/requirements-test.txt
   ```

2. **Application Access**
   - Local: Application running on `http://localhost:5000`
   - Azure: Production app at `https://app.acidtech.fintraqx.com`

3. **Testing Tools**
   - pytest (automated testing)
   - Web browser (manual testing)
   - Network connectivity

## 🚀 Automated QA Testing

### Step 1: Local Development Testing

```bash
# Navigate to project directory
cd C:\Users\Acid Acct1\Documents\Cash_Flow_APP\AcitechAppServ

# Ensure app is running locally first
python startup.py  # In one terminal

# Run QA tests in another terminal
pytest -v tests/test_routes_qa.py
```

**Expected Output:**
```
✅ PASSED: Landing page loads correctly
✅ PASSED: Dashboard loads with masterlayout and Chart.js  
✅ PASSED: Data Import loads with CSV upload interface
✅ PASSED: All routes responding correctly
```

### Step 2: Azure Production Testing

```bash
# Test against Azure production
BASE_URL=https://app.acidtech.fintraqx.com pytest -v tests/test_routes_qa.py

# Generate detailed HTML report
BASE_URL=https://app.acidtech.fintraqx.com pytest -v tests/test_routes_qa.py --html=qa_report.html --self-contained-html
```

### Step 3: Interpret Results

#### ✅ Success Indicators
- All tests show "PASSED" status
- No HTTP 500 errors
- Bootstrap 5 detected in responses
- Chart.js integration confirmed
- Response times under 10 seconds

#### ❌ Failure Indicators  
- Any test shows "FAILED" status
- HTTP 404/500 errors detected
- Missing Bootstrap components
- Tailwind CSS references found
- Response timeouts

## 🔍 Manual QA Testing

### Critical User Journeys

#### 1. Navigation Testing
- [ ] **Sidebar Navigation**: Click all menu items
- [ ] **Mobile Responsiveness**: Test on mobile/tablet sizes
- [ ] **Collapse Functionality**: Sidebar toggles correctly

#### 2. Dashboard Validation
- [ ] **KPI Cards**: All cards display data correctly
- [ ] **Charts**: Chart.js visualizations render
- [ ] **Responsive Layout**: Components adapt to screen size

#### 3. Data Import Testing
- [ ] **CSV Upload**: Upload functionality works
- [ ] **Progress Indicators**: Upload progress displays
- [ ] **Form Validation**: Error handling works correctly

#### 4. Module Pages Testing
Visit each module and verify:
- [ ] **Accounts Payable** (`/accounts-payable`)
- [ ] **Accounts Receivable** (`/accounts-receivable`)  
- [ ] **Purchase Orders** (`/purchase-orders`)
- [ ] **Reports** (`/reports`)

### Visual Design Validation

#### Bootstrap 5 Components Check
- [ ] **Cards**: Professional styling with shadows
- [ ] **Forms**: Bootstrap form controls
- [ ] **Buttons**: Consistent button styles
- [ ] **Tables**: Responsive table design
- [ ] **Alerts**: Toast notifications work

#### Master Layout Verification
- [ ] **Header**: Consistent across all pages
- [ ] **Sidebar**: Same navigation everywhere
- [ ] **Footer**: Properly positioned
- [ ] **Content Area**: Proper spacing and alignment

## 🐛 Troubleshooting Common Issues

### Issue 1: Connection Refused
**Problem**: `requests.exceptions.ConnectionError`  
**Solution**: Ensure the application is running on the target URL

### Issue 2: Template Errors
**Problem**: Jinja2 template not found  
**Solution**: Verify templates exist in correct directories:
```
templates/
├── masterlayout.html
├── dashboard.html  
├── data_import/index.html
└── [other templates]
```

### Issue 3: Bootstrap Not Loading
**Problem**: Tests fail with "Bootstrap 5 not found"  
**Solution**: Check CDN links in masterlayout.html:
```html
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js">
```

### Issue 4: Performance Issues
**Problem**: Response times exceed 10 seconds  
**Solution**: Check Azure App Service scaling and database performance

## 📊 QA Checklist

### Pre-Migration Cleanup ✅
- [x] All HTML removed from route functions
- [x] Templates use masterlayout.html inheritance
- [x] Bootstrap 5 CDN links properly configured
- [x] Chart.js integration implemented

### Post-Migration Validation ✅  
- [x] All 8 routes tested and functional
- [x] No Tailwind CSS dependencies remain
- [x] Responsive design works across devices
- [x] Performance benchmarks met

### Production Readiness ✅
- [x] Azure deployment successful
- [x] Database connections stable  
- [x] File uploads working
- [x] User authentication functional

## 🎉 Success Criteria

### Automated Testing
- **100% Test Pass Rate**: All pytest tests pass
- **Response Time**: All routes < 10 seconds
- **Zero Errors**: No HTTP 4xx/5xx errors
- **Content Validation**: Required elements present

### Manual Testing  
- **UI Consistency**: All pages use master layout
- **Functionality**: All features work as expected
- **Responsiveness**: Mobile/tablet compatibility
- **User Experience**: Smooth navigation and interactions

## 📞 Support and Escalation

### Test Failures
1. **Review logs**: Check pytest output for specific errors
2. **Check application logs**: Review Azure Application Insights
3. **Validate environment**: Ensure all dependencies installed
4. **Escalate if needed**: Contact development team

### Documentation Issues
- Update this guide with new findings
- Document any environment-specific configurations
- Maintain troubleshooting section

---

## 📝 QA Test Execution Log

**Template for QA Sessions:**

```
QA Session: [Date]
Tester: [Name]
Environment: [Local/Azure]
Version: v1.1.0

Automated Tests Results:
□ test_landing_page: PASS/FAIL
□ test_dashboard_route: PASS/FAIL  
□ test_data_import_route: PASS/FAIL
□ test_accounts_payable_route: PASS/FAIL
□ test_accounts_receivable_route: PASS/FAIL
□ test_purchase_orders_route: PASS/FAIL
□ test_reports_route: PASS/FAIL
□ test_test_layout_route: PASS/FAIL

Manual Tests Results:
□ Navigation: PASS/FAIL
□ Dashboard: PASS/FAIL
□ Data Import: PASS/FAIL
□ All Modules: PASS/FAIL
□ Mobile Responsive: PASS/FAIL

Overall Status: PASS/FAIL
Issues Found: [List any issues]
Action Required: [Next steps]
```

---

**Created**: 2025-01-08  
**Version**: 1.0  
**For**: Master Layout System Migration QA

🤖 *Generated with [Claude Code](https://claude.ai/code)*