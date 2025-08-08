-- ===================================================================
-- MIGRATION: ADD CLASSIFICATION FIELDS TO BANK_TRANSACTIONS TABLE
-- Date: 2025-08-08
-- Purpose: Extend BankTransaction model with accounting classification fields
-- Impact: Adds 20+ new nullable fields to existing table
-- Data Safety: PRESERVES all existing 594 transactions
-- ===================================================================

-- Begin transaction for rollback safety
BEGIN TRANSACTION;

-- Backup existing data count for verification
-- Expected: 594 transactions in Revenue 4717

-- ===================================================================
-- ENHANCED TRANSACTION CLASSIFICATION FIELDS
-- ===================================================================

-- Enhanced transaction classification
ALTER TABLE bank_transactions ADD COLUMN transaction_subtype VARCHAR(50);
-- Options: "DEPOSIT", "PAYMENT", "FEE", "INTEREST", "TRANSFER"

ALTER TABLE bank_transactions ADD COLUMN business_category VARCHAR(100);
-- Options: "REVENUE", "OPERATING_EXPENSE", "CAPITAL_EXPENSE", "TAX"

ALTER TABLE bank_transactions ADD COLUMN gl_account_code VARCHAR(20);
-- Chart of Accounts reference: "4000", "6000", etc.

-- ===================================================================
-- INTERNAL TRANSFER FIELDS
-- ===================================================================

ALTER TABLE bank_transactions ADD COLUMN is_internal_transfer BOOLEAN DEFAULT FALSE;
ALTER TABLE bank_transactions ADD COLUMN source_account VARCHAR(100);
ALTER TABLE bank_transactions ADD COLUMN target_account VARCHAR(100);
ALTER TABLE bank_transactions ADD COLUMN transfer_reference VARCHAR(100);

-- ===================================================================
-- CREDIT CARD SPECIFIC FIELDS (Capital One - cuts 11th each month)
-- ===================================================================

ALTER TABLE bank_transactions ADD COLUMN is_credit_card_transaction BOOLEAN DEFAULT FALSE;
ALTER TABLE bank_transactions ADD COLUMN credit_card_cycle_date DATE;
-- Capital One cycle cut date (11th of each month)

ALTER TABLE bank_transactions ADD COLUMN credit_card_due_date DATE;
-- Payment due date (~25 days after cycle cut)

ALTER TABLE bank_transactions ADD COLUMN is_credit_card_payment BOOLEAN DEFAULT FALSE;
-- TRUE when paying TO the credit card

-- ===================================================================
-- ENHANCED MERCHANT/VENDOR INFORMATION
-- ===================================================================

ALTER TABLE bank_transactions ADD COLUMN merchant_name VARCHAR(200);
-- Clean, standardized merchant name

ALTER TABLE bank_transactions ADD COLUMN merchant_category VARCHAR(100);
-- Categories: "RESTAURANT", "GAS_STATION", "OFFICE_SUPPLIES", etc.

ALTER TABLE bank_transactions ADD COLUMN vendor_tax_id VARCHAR(20);
-- For 1099 tracking purposes

-- ===================================================================
-- TAX AND COMPLIANCE FIELDS
-- ===================================================================

ALTER TABLE bank_transactions ADD COLUMN is_tax_deductible BOOLEAN DEFAULT FALSE;
-- Business expense deductibility flag

ALTER TABLE bank_transactions ADD COLUMN tax_category VARCHAR(50);
-- Categories: "MEALS", "TRAVEL", "OFFICE", "VEHICLE", "PAYROLL"

ALTER TABLE bank_transactions ADD COLUMN requires_receipt BOOLEAN DEFAULT FALSE;
-- Receipt requirement flag

ALTER TABLE bank_transactions ADD COLUMN receipt_status VARCHAR(20) DEFAULT 'NOT_REQUIRED';
-- Status: "NOT_REQUIRED", "REQUIRED", "RECEIVED", "MISSING"

-- ===================================================================
-- CLASSIFICATION CONTROL FIELDS
-- ===================================================================

ALTER TABLE bank_transactions ADD COLUMN is_classified BOOLEAN DEFAULT FALSE;
-- Master classification status flag

ALTER TABLE bank_transactions ADD COLUMN classification_confidence NUMERIC(3, 2);
-- Confidence score: 0.00 to 1.00

ALTER TABLE bank_transactions ADD COLUMN classification_method VARCHAR(20);
-- Method: "MANUAL", "RULE_BASED", "ML", "IMPORTED"

ALTER TABLE bank_transactions ADD COLUMN needs_review BOOLEAN DEFAULT FALSE;
-- Manual review required flag

ALTER TABLE bank_transactions ADD COLUMN review_notes TEXT;
-- Notes for manual review

-- ===================================================================
-- ENHANCED RECONCILIATION FIELDS
-- ===================================================================

ALTER TABLE bank_transactions ADD COLUMN is_reconciled BOOLEAN DEFAULT FALSE;
-- Bank reconciliation status

ALTER TABLE bank_transactions ADD COLUMN reconciliation_date DATE;
-- Date when reconciled

ALTER TABLE bank_transactions ADD COLUMN reconciliation_batch_id VARCHAR(50);
-- Reconciliation batch reference

-- ===================================================================
-- METADATA UPDATE
-- ===================================================================

ALTER TABLE bank_transactions ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP;
-- Track when record was last updated

-- ===================================================================
-- PERFORMANCE INDEXES
-- ===================================================================

-- Index for classification status queries
CREATE INDEX IF NOT EXISTS idx_bank_transactions_classification 
ON bank_transactions(is_classified, needs_review);

-- Index for business category analysis
CREATE INDEX IF NOT EXISTS idx_bank_transactions_business_category 
ON bank_transactions(business_category, transaction_date);

-- Index for credit card transactions
CREATE INDEX IF NOT EXISTS idx_bank_transactions_credit_card 
ON bank_transactions(is_credit_card_transaction, credit_card_cycle_date);

-- Index for tax deductible expenses
CREATE INDEX IF NOT EXISTS idx_bank_transactions_tax_deductible 
ON bank_transactions(is_tax_deductible, tax_category);

-- Index for reconciliation status
CREATE INDEX IF NOT EXISTS idx_bank_transactions_reconciliation 
ON bank_transactions(is_reconciled, reconciliation_date);

-- Index for merchant analysis
CREATE INDEX IF NOT EXISTS idx_bank_transactions_merchant 
ON bank_transactions(merchant_name, merchant_category);

-- ===================================================================
-- DATA VERIFICATION
-- ===================================================================

-- Verify no data loss occurred
SELECT 'Data Verification:' as status;
SELECT COUNT(*) as total_transactions FROM bank_transactions;
SELECT account_name, COUNT(*) as count FROM bank_transactions GROUP BY account_name;

-- Verify new fields were added
SELECT 'New Fields Added:' as status;
PRAGMA table_info(bank_transactions);

-- ===================================================================
-- INITIAL DATA POPULATION (Optional - can be run separately)
-- ===================================================================

-- Initialize all existing transactions as unclassified
UPDATE bank_transactions 
SET is_classified = FALSE, 
    classification_method = NULL,
    needs_review = FALSE
WHERE is_classified IS NULL;

-- Set default receipt status for existing transactions
UPDATE bank_transactions 
SET receipt_status = 'NOT_REQUIRED'
WHERE receipt_status IS NULL;

-- Mark Capital One transactions based on account name
UPDATE bank_transactions 
SET is_credit_card_transaction = TRUE
WHERE account_name LIKE '%Capital One%';

-- Commit the transaction
COMMIT;

-- ===================================================================
-- MIGRATION COMPLETION LOG
-- ===================================================================

SELECT 'MIGRATION COMPLETED SUCCESSFULLY' as status;
SELECT 'Total transactions preserved: ' || COUNT(*) as result FROM bank_transactions;
SELECT 'Classification fields added: 20+' as result;
SELECT 'Performance indexes created: 6' as result;
SELECT datetime('now', 'localtime') as completion_time;

-- ===================================================================
-- ROLLBACK SCRIPT (for emergencies)
-- ===================================================================

/*
-- EMERGENCY ROLLBACK (run only if needed)
BEGIN TRANSACTION;

-- Remove all added columns (SQLite limitations - would need to recreate table)
-- This is why we backup data first!

-- Alternative: Reset all new fields to NULL
UPDATE bank_transactions SET 
    transaction_subtype = NULL,
    business_category = NULL,
    gl_account_code = NULL,
    is_internal_transfer = FALSE,
    source_account = NULL,
    target_account = NULL,
    transfer_reference = NULL,
    is_credit_card_transaction = FALSE,
    credit_card_cycle_date = NULL,
    credit_card_due_date = NULL,
    is_credit_card_payment = FALSE,
    merchant_name = NULL,
    merchant_category = NULL,
    vendor_tax_id = NULL,
    is_tax_deductible = FALSE,
    tax_category = NULL,
    requires_receipt = FALSE,
    receipt_status = 'NOT_REQUIRED',
    is_classified = FALSE,
    classification_confidence = NULL,
    classification_method = NULL,
    needs_review = FALSE,
    review_notes = NULL,
    is_reconciled = FALSE,
    reconciliation_date = NULL,
    reconciliation_batch_id = NULL;

COMMIT;
*/